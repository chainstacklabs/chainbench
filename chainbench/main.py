import logging
import os
import shlex
import subprocess
import sys
from multiprocessing import Process
from pathlib import Path

import click
from locust import runners

from chainbench.util.cli import (
    ContextData,
    ensure_results_dir,
    get_base_path,
    get_master_command,
    get_profile_path,
    get_worker_command,
)
from chainbench.util.monitor import monitors
from chainbench.util.notify import NoopNotifier, Notifier

# Default values for arguments
MASTER_HOST = "127.0.0.1"
MASTER_PORT = "5557"
WORKER_COUNT = 16
TEST_TIME = "1h"
USERS = 1000
SPAWN_RATE = 10
LOG_LEVEL = "DEBUG"
DEFAULT_PROFILE = "ethereum.general"
NOTIFY_URL_TEMPLATE = "https://ntfy.sh/{topic}"
runners.HEARTBEAT_INTERVAL = 60

logger = logging.getLogger(__name__)


@click.group(
    help="Tool for flexible blockchain infrastructure benchmarking.",
)
@click.version_option(message="%(prog)s-%(version)s")
@click.pass_context
def cli(ctx: click.Context):
    ctx.obj = ContextData()


@cli.command(
    help="Start the test using the configured profile. "
    "By default, the results are saved in the "
    "./results/{profile}/{YYYY-mm-dd_HH-MM-SS} directory.",
)
@click.option(
    "-p",
    "--profile",
    default=DEFAULT_PROFILE,
    help="Profile to run",
    show_default=True,
)
@click.option(
    "-d", "--profile-dir", default=None, type=click.Path(), help="Profile directory"
)
@click.option(
    "-H", "--host", default=MASTER_HOST, help="Host to run on", show_default=True
)
@click.option(
    "-P", "--port", default=MASTER_PORT, help="Port to run on", show_default=True
)
@click.option(
    "-w",
    "--workers",
    default=WORKER_COUNT,
    help="Number of workers to run",
    show_default=True,
)
@click.option(
    "-t", "--test-time", default=TEST_TIME, help="Test time", show_default=True
)
@click.option(
    "-u", "--users", default=USERS, help="Target number of users", show_default=True
)
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
    type=click.Path(),
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
    type=click.Choice(["head-lag-monitor"], case_sensitive=False),
    multiple=True,
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
    help="Exclude tasks tagged with custom tags from the test. "
    "You may specify this option multiple times",
    multiple=True,
)
@click.option(
    "--timescale", is_flag=True, help="Export data to PG with timescale extension"
)
@click.option(
    "--pg-host", default=None, help="Hostname of PG instance with timescale extension"
)
@click.option(
    "--pg-port",
    default=5432,
    help="Port of PG instance with timescale extension",
    show_default=True,
)
@click.option(
    "--pg-username", default="postgres", help="PG username", show_default=True
)
@click.option("--pg-password", default=None, help="PG password")
@click.pass_context
def start(
    ctx: click.Context,
    profile: str,
    profile_dir: Path | None,
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
    debug_trace_methods: bool,
    exclude_tags: list[str],
    timescale: bool,
    pg_host: str | None,
    pg_port: int,
    pg_username: str,
    pg_password: str | None,
):
    if notify:
        click.echo(f"Notify when test is finished using topic: {notify}")
        notifier = Notifier(topic=notify)
    else:
        notifier = NoopNotifier()

    ctx.obj.notifier = notifier

    if headless and target is None:
        click.echo("Target is required when running in headless mode")
        sys.exit(1)

    if timescale and any(
        pg_arg is None for pg_arg in (pg_host, pg_port, pg_username, pg_password)
    ):
        click.echo(
            "PG connection parameters are required "
            "when --timescale flag is used: pg_host, pg_port, pg_username, pg_password"
        )
        sys.exit(1)

    if not profile_dir:
        profile_dir = get_base_path(__file__)

    profile_path = get_profile_path(profile_dir, profile)

    if not profile_path.exists():
        click.echo(f"Profile file {profile_path} does not exist")
        sys.exit(1)

    results_dir = Path(results_dir).resolve()

    click.echo(f"Results directory: {results_dir}")

    results_path = ensure_results_dir(
        profile=profile, parent_dir=results_dir, run_id=run_id
    )

    click.echo(f"Results will be saved to {results_path}")

    custom_exclude_tags: list[str] = []
    if exclude_tags:
        for tag in exclude_tags:
            custom_exclude_tags.append(tag)

    if not debug_trace_methods:
        custom_exclude_tags = custom_exclude_tags + ["trace", "debug"]

    # Start the Locust master
    master_command = get_master_command(
        profile_path=profile_path,
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
        exclude_tags=custom_exclude_tags,
        timescale=timescale,
        pg_host=pg_host,
        pg_port=pg_port,
        pg_username=pg_username,
        pg_password=pg_password,
    )
    if headless:
        click.echo(f"Starting master in headless mode for {profile}")
    else:
        click.echo(f"Starting master for {profile}")

    is_posix = os.name == "posix"

    master_args = shlex.split(master_command, posix=is_posix)
    master_process = subprocess.Popen(master_args)
    ctx.obj.master = master_process

    # Start the Locust workers
    for worker_id in range(workers):
        worker_command = get_worker_command(
            profile_path=profile_path,
            host=host,
            port=port,
            results_path=results_path,
            headless=headless,
            target=target,
            worker_id=worker_id,
            log_level=log_level,
            exclude_tags=custom_exclude_tags,
            timescale=timescale,
            pg_host=pg_host,
            pg_port=pg_port,
            pg_username=pg_username,
            pg_password=pg_password,
        )
        worker_args = shlex.split(worker_command, posix=is_posix)
        worker_process = subprocess.Popen(worker_args)
        ctx.obj.workers.append(worker_process)
        click.echo(f"Starting worker {worker_id + 1} for {profile}")
    if headless:
        click.echo(f"Running test in headless mode for {profile}")
        ctx.obj.notifier.notify(
            title="Test started",
            message=f"Running test in headless mode for {profile}",
            tags=["loudspeaker"],
        )
    else:
        # Print out the URL to access the test
        click.echo(f"Run test: http://{host}:8089 {profile}")

    unique_monitors: set[str] = set(monitor)
    for m in unique_monitors:
        p = Process(target=monitors[m], args=(target, results_path, test_time))
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

    ctx.obj.notifier.notify(
        title="Test finished", message=f"Test finished for {profile}", tags=["tada"]
    )


if __name__ == "__main__":
    cli()
