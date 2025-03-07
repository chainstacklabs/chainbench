import os
import shlex
import subprocess
import sys
from multiprocessing import Process
from pathlib import Path

import click
import gevent.pool
from click import Context, Parameter
from locust.argument_parser import parse_locustfile_paths
from locust.util.load_locustfile import load_locustfile

from chainbench.user import EvmUser, SolanaUser, get_subclass_tasks
from chainbench.user.common import all_method_classes, all_methods
from chainbench.util.cli import (
    ContextData,
    LocustOptions,
    ensure_results_dir,
    get_base_path,
    get_profile_path,
    get_profiles,
)
from chainbench.util.monitor import monitors
from chainbench.util.notify import NoopNotifier, Notifier

# Default values for arguments
MASTER_HOST = "127.0.0.1"
MASTER_PORT = "5557"
WORKER_COUNT = 8
TEST_TIME = "5m"
USERS = 100
SPAWN_RATE = 10
LOG_LEVEL = "INFO"
DEFAULT_PROFILE = "ethereum.general"
NOTIFY_URL_TEMPLATE = "https://ntfy.sh/{topic}"


@click.group(
    help="Tool for flexible blockchain infrastructure benchmarking.",
)
@click.version_option(message="%(prog)s-%(version)s")
@click.pass_context
def cli(ctx: Context):
    ctx.obj = ContextData()


def validate_method(ctx: Context, param: Parameter, value: str) -> str:
    if value is not None:
        if value not in all_methods.keys():
            raise click.BadParameter(
                f"Method {value} is not supported. " f"Use 'chainbench list methods' to list all available methods."
            )
        if "profile" in ctx.params:
            click.echo("WARNING: Profile and Profile Directory options are ignored when method argument is used.")
    return value


def profile_exists(profile: str, profile_dir: Path) -> None:
    profile_list = get_profiles(profile_dir)
    if profile not in profile_list:
        raise click.BadParameter(
            f"Profile {profile} could not be found in {profile_dir}. "
            f"Use 'chainbench list profiles -d {profile_dir}' to list available profiles."
        )


def validate_profile_dir(ctx: Context, param: Parameter, value: Path) -> Path | None:
    if value is not None:
        profile_dir = Path(value)
        if "profile" in ctx.params:
            profile_exists(ctx.params["profile"], profile_dir)
        return profile_dir
    else:
        return None


def validate_profile(ctx: Context, param: Parameter, value: str) -> str:
    if value is not None:
        if "profile_dir" in ctx.params:
            profile_exists(value, ctx.params["profile_dir"])
        if "method" in ctx.params:
            click.echo("WARNING: Profile and Profile Directory options are ignored when method argument is used.")
    return value


def validate_profile_path(ctx: Context, param: Parameter, value: str) -> str:
    if value is not None:
        if "profile_dir" or "profile" in ctx.params:
            click.echo("WARNING: Profile and Profile Directory options are ignored when --profile-path flag is used.")
        if "method" in ctx.params:
            click.echo("WARNING: Profile and Profile Directory options are ignored when method argument is used.")
        """Validate profile path."""
        abs_profile_path = Path(value).resolve()
        if not abs_profile_path.exists():
            raise FileNotFoundError(f"Profile path not found: {abs_profile_path}")
        profile_exists(abs_profile_path.name.removesuffix(".py"), abs_profile_path.parent)
    return value


@cli.command(
    help="Start a load test on the specified method. "
    "Alternatively, you can specify a profile to run using the --profile option instead. "
    "By default, the results are saved in the "
    "./results/{profile_or_method_name}/{YYYY-mm-dd_HH-MM-SS} directory.",
)
@click.argument("method", default=None, callback=validate_method, required=False)
@click.option(
    "-d",
    "--profile-dir",
    default=None,
    callback=validate_profile_dir,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    help="Profile directory",
)
@click.option(
    "-p",
    "--profile",
    default=None,
    callback=validate_profile,
    help="Profile to run",
    show_default=True,
)
@click.option(
    "--profile-path",
    default=None,
    callback=validate_profile_path,
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    help="Path to profile locustfile to be run. Overrides --profile and --profile-dir options.",
    show_default=True,
)
@click.option(
    "-s",
    "--shape",
    default=None,
    help="Shape of load pattern",
)
@click.option("-H", "--host", default=MASTER_HOST, help="Host to run on", show_default=True)
@click.option("-P", "--port", default=MASTER_PORT, help="Port to run on", show_default=True)
@click.option(
    "-w",
    "--workers",
    default=WORKER_COUNT,
    help="Number of workers to run",
    show_default=True,
)
@click.option("-t", "--test-time", default=TEST_TIME, help="Test time", show_default=True)
@click.option("-u", "--users", default=USERS, help="Target number of users", show_default=True)
@click.option(
    "-r",
    "--spawn-rate",
    default=SPAWN_RATE,
    help="Number of users spawned per second",
    show_default=True,
)
@click.option("--log-level", default=LOG_LEVEL, help="Log level", show_default=True)
@click.option(
    "--results-dir",
    default=Path("results"),
    help="Results directory",
    type=click.Path(dir_okay=True, file_okay=False, writable=True, path_type=Path),
    show_default=True,
)
@click.option("--headless", is_flag=True, help="Run in headless mode")
@click.option("--autoquit", is_flag=True, help="Auto quit after test")
@click.option("--target", default=None, help="Endpoint to test")
@click.option("--run-id", default=None, help="ID of the test")
@click.option("--notify", default=None, help="Notify when test is finished")
@click.option(
    "-m",
    "--monitor",
    default=[],
    help="Add a monitor to collect additional data or metrics. "
    "You may specify this option multiple times for different monitors",
    type=click.Choice(["sync-lag-monitor"], case_sensitive=False),
    multiple=True,
)
@click.option(
    "--batch",
    is_flag=True,
    help="Run tests in batch mode. This will make requests in batches for json-rpc methods. The number of requests in "
    "a batch can be specified using the `--batch-size` flag",
)
@click.option(
    "--batch-size",
    default=10,
    help="The number of requests in " "a batch for json-rpc methods. This flag is only used when `--batch` flag is set",
)
@click.option(
    "--debug-trace-methods",
    is_flag=True,
    help="Enable tasks tagged with debug or trace to be executed",
)
@click.option(
    "-E",
    "--exclude-tags",
    default=[],
    help="Exclude tasks tagged with custom tags from the test. " "You may specify this option multiple times",
    multiple=True,
)
@click.option("--timescale", is_flag=True, help="Export data to PG with timescale extension")
@click.option("--pg-host", default=None, help="Hostname of PG instance with timescale extension")
@click.option(
    "--pg-port",
    default=5432,
    help="Port of PG instance with timescale extension",
    show_default=True,
)
@click.option("--pg-username", default="postgres", help="PG username", show_default=True)
@click.option("--pg-password", default=None, help="PG password")
@click.option("--use-latest-blocks", is_flag=True, help="Uses latest blocks for test data")
@click.option("--size", default=None, help="Set the size of the test data. e.g. --size S")
@click.pass_context
def start(
    ctx: Context,
    profile: str,
    profile_dir: Path | None,
    profile_path: Path | None,
    shape: str | None,
    host: str,
    port: int,
    workers: int,
    test_time: str,
    users: int,
    spawn_rate: int,
    log_level: str,
    results_dir: Path,
    headless: bool,
    autoquit: bool,
    target: str | None,
    run_id: str | None,
    notify: str | None,
    monitor: list[str],
    batch: bool,
    batch_size: int,
    debug_trace_methods: bool,
    exclude_tags: list[str],
    timescale: bool,
    pg_host: str | None,
    pg_port: int,
    pg_username: str,
    pg_password: str | None,
    use_latest_blocks: bool,
    size: str | None,
    method: str | None = None,
) -> None:
    if notify:
        click.echo(f"Notify when test is finished using topic: {notify}")
        notifier = Notifier(topic=notify)
    else:
        notifier = NoopNotifier()

    ctx.obj.notifier = notifier

    if target is None:
        click.echo(
            "Target is required. If running in Web UI mode you may change it later "
            "but it is needed to initialize test data."
        )
        sys.exit(1)

    enable_class_picker = False
    test_by_directory = profile is None and method is None

    if profile_dir is None:
        profile_dir = get_base_path(__file__) / "profile"

    if method:
        final_profile_path = Path(all_methods[method])
    elif profile_path:
        final_profile_path = profile_path
    elif profile:
        final_profile_path = get_profile_path(profile_dir, profile)
    else:
        final_profile_path = profile_dir

    if not final_profile_path.exists():
        click.echo(f"Profile path {final_profile_path} does not exist.")
        sys.exit(1)

    user_classes = {}
    for locustfile in parse_locustfile_paths([final_profile_path.__str__()]):
        _, _user_classes, _ = load_locustfile(locustfile)
        for key, value in _user_classes.items():
            user_classes[key] = value
    test_data_types = set()
    for user_class in user_classes.values():
        test_data_types.add(type(getattr(user_class, "test_data")).__name__)

    if test_by_directory:
        if len(test_data_types) > 1:
            click.echo(
                "Error occurred: Multiple test data types detected. "
                "Specifying a directory that contains load profiles with same test data type "
                "is required if --profile option or method argument is not utilized."
            )
            click.echo("Test data types detected:")
            for test_data_type in test_data_types:
                click.echo(test_data_type)
            sys.exit(1)
        profile = final_profile_path.name
        if not headless:
            enable_class_picker = True

    click.echo(f"Testing target endpoint: {target}")

    if method:
        if headless:
            profile = method
        else:
            profile = "test_method"
        click.echo(f"Testing method: {method}")
        test_plan = method
    else:
        click.echo(f"Testing profile: {profile}")
        test_plan = profile

    if shape is not None:
        shapes_dir = get_base_path(__file__) / "shapes"
        shape_path = get_profile_path(shapes_dir, shape)
        click.echo(f"Using load shape: {shape}")
    else:
        shape_path = None

    results_dir = Path(results_dir).resolve()
    results_path = ensure_results_dir(profile=profile, parent_dir=results_dir, run_id=run_id)

    click.echo(f"Results will be saved to {results_path}")

    if timescale and any(pg_arg is None for pg_arg in (pg_host, pg_port, pg_username, pg_password)):
        click.echo(
            "PG connection parameters are required "
            "when --timescale flag is used: pg_host, pg_port, pg_username, pg_password"
        )
        sys.exit(1)

    custom_exclude_tags: list[str] = []
    if exclude_tags:
        for tag in exclude_tags:
            custom_exclude_tags.append(tag)

    if not debug_trace_methods:
        custom_exclude_tags.extend(["trace", "debug"])

    custom_tags: list[str] = []

    if batch:
        custom_tags = ["batch_single" if method else "batch"]
    else:
        if method:
            custom_tags.append("single")
        else:
            custom_exclude_tags.append("single")
        custom_exclude_tags.extend(["batch", "batch_single"])

    locust_options = LocustOptions(
        profile_path=final_profile_path,
        host=host,
        port=port,
        test_time=test_time,
        users=users,
        spawn_rate=spawn_rate,
        log_level=log_level,
        results_path=results_path,
        workers=workers,
        headless=headless,
        target=target,
        custom_tags=custom_tags,
        exclude_tags=custom_exclude_tags,
        shape_path=shape_path,
        timescale=timescale,
        pg_host=pg_host,
        pg_port=pg_port,
        pg_username=pg_username,
        pg_password=pg_password,
        override_plan_name=test_plan,
        use_latest_blocks=use_latest_blocks,
        size=size,
        method=method,
        enable_class_picker=enable_class_picker,
        batch_size=batch_size,
    )
    # Start the Locust master
    master_command = locust_options.get_master_command()

    if headless:
        click.echo("Starting master in headless mode")
    else:
        click.echo("Starting master")

    is_posix = os.name == "posix"

    master_args = shlex.split(master_command, posix=is_posix)
    master_process = subprocess.Popen(master_args)
    ctx.obj.master = master_process

    # Start the Locust workers
    for worker_id in range(workers):
        worker_command = locust_options.get_worker_command(worker_id=worker_id)
        worker_args = shlex.split(worker_command, posix=is_posix)
        worker_process = subprocess.Popen(worker_args)
        ctx.obj.workers.append(worker_process)
        click.echo(f"Starting worker {worker_id + 1}")
    if headless:
        click.echo("\nRunning test in headless mode\n")
        ctx.obj.notifier.notify(
            title="Test started",
            message=f"Running test in headless mode for {profile}",
            tags=["loudspeaker"],
        )

    if list(test_data_types)[0] == "SolanaTestData":
        user: type[SolanaUser] | type[EvmUser] = SolanaUser
    else:
        user = EvmUser

    unique_monitors: set[str] = set(monitor)
    for m in unique_monitors:
        p = Process(target=monitors[m], args=(user, target, results_path, test_time))
        click.echo(f"Starting monitor {m}")
        p.start()
        ctx.obj.monitors.append(p)

    for process in ctx.obj.workers:
        process.wait()

    for process in ctx.obj.monitors:
        process.join()

    if autoquit:
        ctx.obj.master.wait()
        click.echo("Quitting...")
        ctx.obj.master.terminate()

    ctx.obj.notifier.notify(title="Test finished", message=f"Test finished for {profile}", tags=["tada"])


def validate_clients(ctx: Context, param: Parameter, value: str) -> list[str]:
    from chainbench.tools.discovery.rpc import RpcDiscovery

    if value is not None:
        input_client_list = value.split(",")
        client_list: list[str] = []
        for client in RpcDiscovery.get_clients():
            client_list.extend(client.get_cli_argument_names())
        for client_name in input_client_list:
            if client_name not in client_list:
                raise click.BadParameter(
                    f"Client {client_name} is not supported. "
                    f"Use 'chainbench list clients' to list all available clients."
                )
    else:
        click.echo("Defaulting to ethereum execution api methods.")
        input_client_list = ["eth"]
    return input_client_list


@cli.command(
    help="Discover methods available on target endpoint.\n"
    "Example usage:\n"
    "chainbench discover https://eth-rpc-endpoint --clients geth,erigon",
)
@click.argument("endpoint", default=None)
@click.option(
    "--clients",
    callback=validate_clients,
    default=None,
    help="List of methods used to test the endpoint will "
    "be based on the clients specified here, default to eth. e.g. --clients eth,bsc.\n",
)
def discover(endpoint: str | None, clients: list[str]) -> None:
    if not endpoint:
        click.echo("Target endpoint is required.")
        sys.exit(1)

    from chainbench.tools.discovery.rpc import RpcDiscovery

    rpc_discovery = RpcDiscovery(endpoint, clients)
    click.echo(f"Please wait, discovering methods available on {endpoint}...")

    def get_discovery_result(method: str) -> None:
        result = rpc_discovery.discover_method(method)
        click.echo(result.to_string())

    pool = gevent.pool.Pool(20)
    for method in rpc_discovery.methods:
        pool.spawn(get_discovery_result, method)

    pool.join()
    rpc_discovery.http.close()


@cli.group(name="list", help="Lists values of the given type.")
def _list() -> None:
    pass


@_list.command(
    help="Lists all available client options for method discovery.",
)
def clients() -> None:
    from chainbench.tools.discovery.rpc import RpcDiscovery

    for client in RpcDiscovery.get_clients():
        for unique_client in client.get_name_and_version():
            click.echo(unique_client)


@_list.command(
    help="Lists all available load profiles.",
)
@click.option(
    "-d",
    "--profile-dir",
    default=get_base_path(__file__) / "profile",
    callback=validate_profile_dir,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    help="Profile directory",
)
def profiles(profile_dir: Path) -> None:
    for profile in get_profiles(profile_dir):
        click.echo(profile)


@_list.command(
    help="Lists all available load shapes.",
)
def shapes() -> None:
    for shape in get_profiles(get_base_path(__file__) / "shapes"):
        click.echo(shape)


@_list.command(
    help="Lists all available methods.",
)
def methods() -> None:
    for method_class in all_method_classes:
        click.echo(f"\nMethods for {method_class.__name__}: ")
        task_list = get_subclass_tasks(method_class)
        for task in task_list:
            click.echo(f"- {method_class.task_to_method(task.name)}")


if __name__ == "__main__":
    cli()
