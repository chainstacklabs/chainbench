import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from geventhttpclient import URL

from chainbench.util.http import (
    HttpClient,
    HttpErrorLevel,
    HttpStatusError,
    JsonRpcError,
)
from chainbench.util.notify import NoopNotifier, Notifier


def get_base_path(src_path: str | Path) -> Path:
    """Get base path."""
    curr_path = Path(src_path).resolve()
    base_path = curr_path.parent
    return base_path


def get_profile_path(base_path: Path, profile: str) -> Path:
    """Get profile path."""
    profile_parts = profile.split(".")
    profile_path = base_path / f"{'/'.join(profile_parts)}.py"
    return profile_path


def get_profiles(profile_dir: Path) -> list[str]:
    """Get list of profiles in given directory."""
    from locust.argument_parser import find_locustfiles

    result = []
    for locustfile in find_locustfiles([profile_dir.__str__()], True):
        locustfile_path = Path(locustfile).relative_to(profile_dir)
        if locustfile_path.parent.__str__() != ".":
            result.append(".".join(locustfile_path.parts[:-1]) + "." + locustfile_path.parts[-1][:-3])
        else:
            result.append(locustfile_path.parts[0][:-3])
    return result


def generate_unique_dir_name() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def ensure_results_dir(profile: str, parent_dir: Path, run_id: str | None = None) -> Path:
    if run_id is not None:
        results_dir = (parent_dir / run_id).resolve()
    else:
        results_dir = (parent_dir / profile / generate_unique_dir_name()).resolve()
    if not results_dir.exists():
        results_dir.mkdir(parents=True, exist_ok=True)

    return results_dir


def get_timescale_args(
    pg_host: str | None,
    pg_port: int | None,
    pg_username: str | None,
    pg_password: str | None,
) -> str:
    return f" --timescale --pghost={pg_host} --pgport={pg_port}" f" --pgpassword={pg_password} --pguser={pg_username}"


def get_url_domain(target_url: str) -> str:
    """Get domain from URL."""
    return URL(target_url).host


def get_target_client_version(target_url: str) -> str:
    """Get client version from target URL."""
    http = HttpClient(target_url, error_level=HttpErrorLevel.ClientError)

    def _get_version_rpc(_method: str, _path: str) -> str:
        try:
            _response = http.make_rpc_call(method=_method, path=_path)
            return str(_response)
        except (JsonRpcError, HttpStatusError):
            return "unknown"

    rpc_methods = [
        "web3_clientVersion",
        "getVersion",
        ("pathfinder_version", "/rpc/pathfinder/v0.1"),
        "juno_version",
        "nodeVersion",
    ]

    for rpc_method in rpc_methods:
        if isinstance(rpc_method, tuple):
            method, path = rpc_method
        else:
            method = rpc_method
            path = ""
        version = _get_version_rpc(method, path)
        if version != "unknown":
            return version

    try:
        response = http.get("eth/v1/node/version")
        return response.json["data"]["version"]
    except (JsonRpcError, HttpStatusError):
        return "unknown"


@dataclass
class LocustOptions:
    profile_path: Path
    host: str
    port: int
    users: int
    workers: int
    spawn_rate: int
    test_time: str
    log_level: str
    results_path: Path
    exclude_tags: list[str]
    target: str
    headless: bool = False
    timescale: bool = False
    pg_host: str | None = None
    pg_port: int | None = None
    pg_username: str | None = None
    pg_password: str | None = None
    override_plan_name: str | None = None
    use_latest_blocks: bool = False
    size: str | None = None
    method: str | None = None
    enable_class_picker: bool = False

    def get_master_command(self) -> str:
        """Generate master command."""
        command = (
            f"locust -f {self.profile_path} --master "
            f"--master-bind-host {self.host} --master-bind-port {self.port} "
            f"--web-host {self.host} "
            f"-u {self.users} -r {self.spawn_rate} --run-time {self.test_time} "
            f"--html {self.results_path}/report.html --csv {self.results_path}/report.csv "
            f"--logfile {self.results_path}/report.log "
            f"--loglevel {self.log_level} --expect-workers {self.workers} "
            f"--size {self.size}"
        )

        if self.enable_class_picker:
            command += " --class-picker"

        return self.get_extra_options(command)

    def get_worker_command(self, worker_id: int = 0) -> str:
        """Generate worker command."""
        command = (
            f"locust -f {self.profile_path} --worker --master-host {self.host} --master-port {self.port} "
            f"--logfile {self.results_path}/worker_{worker_id}.log --loglevel {self.log_level}"
        )
        return self.get_extra_options(command)

    def get_extra_options(self, command: str):
        if self.timescale:
            command += get_timescale_args(self.pg_host, self.pg_port, self.pg_username, self.pg_password)
            if self.override_plan_name is not None:
                command += f" --override-plan-name {self.override_plan_name}"
            from importlib import metadata

            command += f" --test-version chainbench-{metadata.version('chainbench')}"
            command += f' --description "{get_url_domain(self.target)} [{get_target_client_version(self.target)}]"'

        if self.target is not None:
            command += f" --host {self.target}"

        if self.headless:
            command += " --headless"

        if len(self.exclude_tags) > 0:
            command += f" --exclude-tags {' '.join(self.exclude_tags)}"

        if self.use_latest_blocks:
            command += " --use-latest-blocks True"

        if self.method is not None:
            command += f" --method {self.method}"
        return command


@dataclass
class ContextData:
    workers: list[subprocess.Popen] = field(default_factory=list)
    master: subprocess.Popen | None = None
    monitors: list[subprocess.Popen] = field(default_factory=list)
    notifier: Notifier = field(default_factory=NoopNotifier)
