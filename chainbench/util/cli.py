import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

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


def get_subclass_methods(cls: type) -> list[str]:
    methods = set(dir(cls))
    unique_subclass_methods = methods.difference(*(dir(base) for base in cls.__bases__))
    return sorted(list(unique_subclass_methods))


def task_to_method(task: str) -> str:
    task_name_stripped = task.replace("_task", "")
    words = task_name_stripped.split("_")
    namespace = words[0]
    method = "".join([words[1]] + [word.capitalize() for word in words[2:]])
    return f"{namespace}_{method}"


def method_to_task(method: str) -> str:
    words = method.split("_")
    namespace = words[0]
    method_name_split = re.split("(?<=.)(?=[A-Z])", words[1])
    method_name = "_".join([word.lower() for word in method_name_split])
    return f"{namespace}_{method_name}_task"


def get_timescale_args(
    pg_host: str | None,
    pg_port: int | None,
    pg_username: str | None,
    pg_password: str | None,
) -> str:
    return f" --timescale --pghost={pg_host} --pgport={pg_port}" f" --pgpassword={pg_password} --pguser={pg_username}"


def get_master_command(
    profile_path: Path,
    host: str,
    port: int,
    users: int,
    workers: int,
    spawn_rate: int,
    test_time: str,
    log_level: str,
    results_path: Path,
    exclude_tags: list[str],
    target: str | None = None,
    headless: bool = False,
    timescale: bool = False,
    pg_host: str | None = None,
    pg_port: int | None = None,
    pg_username: str | None = None,
    pg_password: str | None = None,
    use_latest_blocks: bool = False,
    size: str | None = None,
    method: str | None = None,
    enable_class_picker: bool = False,
) -> str:
    """Generate master command."""
    command = (
        f"locust -f {profile_path} --master "
        f"--master-bind-host {host} --master-bind-port {port} "
        f"--web-host {host} "
        f"-u {users} -r {spawn_rate} --run-time {test_time} "
        f"--html {results_path}/report.html --csv {results_path}/report.csv "
        f"--logfile {results_path}/report.log "
        f"--loglevel {log_level} --expect-workers {workers} "
        f"--size {size}"
    )

    if timescale:
        command += get_timescale_args(pg_host, pg_port, pg_username, pg_password)

    if target is not None:
        command += f" --host {target}"

    if headless:
        command += " --headless"

    if len(exclude_tags) > 0:
        command += f" --exclude-tags {' '.join(exclude_tags)}"

    if use_latest_blocks:
        command += " --use-latest-blocks True"

    if method is not None:
        command += f" --method {method}"

    if enable_class_picker:
        command += " --class-picker"
    return command


def get_worker_command(
    profile_path: Path,
    host: str,
    port: int,
    results_path: Path,
    log_level: str,
    exclude_tags: list[str],
    target: str | None = None,
    headless: bool = False,
    worker_id: int = 0,
    timescale: bool = False,
    pg_host: str | None = None,
    pg_port: int | None = None,
    pg_username: str | None = None,
    pg_password: str | None = None,
    use_latest_blocks: bool = False,
    method: str | None = None,
) -> str:
    """Generate worker command."""
    command = (
        f"locust -f {profile_path} --worker --master-host {host} --master-port {port} "
        f"--logfile {results_path}/worker_{worker_id}.log --loglevel {log_level}"
    )

    if timescale:
        command += get_timescale_args(pg_host, pg_port, pg_username, pg_password)

    if target is not None:
        command += f" --host {target}"

    if headless:
        command += " --headless"

    if len(exclude_tags) > 0:
        command += f" --exclude-tags {' '.join(exclude_tags)}"

    if use_latest_blocks:
        command += " --use-latest-blocks True"

    if method is not None:
        command += f" --method {method}"
    return command


@dataclass
class ContextData:
    workers: list[subprocess.Popen] = field(default_factory=list)
    master: subprocess.Popen | None = None
    monitors: list[subprocess.Popen] = field(default_factory=list)
    notifier: Notifier = field(default_factory=NoopNotifier)
