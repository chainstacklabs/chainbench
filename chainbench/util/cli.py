import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from chainbench.util.notify import NoopNotifier, Notifier


def get_base_path(src_path: str | Path) -> Path:
    """Get base path."""
    curr_path = Path(src_path).resolve()
    base_path = curr_path.parent / "profile"
    return base_path


def get_profile_path(base_path: Path, profile: str) -> Path:
    """Get profile path."""
    subdir, _, profile = profile.rpartition(".")
    if subdir:
        profile_path = base_path / subdir / f"{profile}.py"
    else:
        profile_path = base_path / f"{profile}.py"
    return profile_path


def generate_unique_dir_name() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def ensure_results_dir(
    profile: str, parent_dir: Path, run_id: str | None = None
) -> Path:
    if run_id is not None:
        results_dir = (parent_dir / run_id).resolve()
    else:
        results_dir = (parent_dir / profile / generate_unique_dir_name()).resolve()
    if not results_dir.exists():
        results_dir.mkdir(parents=True, exist_ok=True)

    return results_dir


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
    target: str | None = None,
    headless: bool = False,
    exclude_tags: list[str] | None = None,
) -> str:
    """Generate master command."""
    command = (
        f"locust -f {profile_path} --master --host {host} "
        f"--master-bind-host {host} --master-bind-port {port} "
        f"-u {users} -r {spawn_rate} --run-time {test_time} "
        f"--html {results_path}/report.html --csv {results_path}/report.csv "
        f"--logfile {results_path}/report.log "
        f"--loglevel {log_level} --expect-workers {workers}"
    )

    if target is not None:
        command += f" --host {target}"

    if headless:
        command += " --headless"

    if exclude_tags:
        command += f" --exclude-tags {' '.join(exclude_tags)}"

    return command


def get_worker_command(
    profile_path: Path,
    host: str,
    port: int,
    results_path: Path,
    log_level: str,
    target: str | None = None,
    headless: bool = False,
    worker_id: int = 0,
    exclude_tags: list[str] | None = None,
) -> str:
    """Generate worker command."""
    command = (
        f"locust -f {profile_path} --worker --master-host {host} --master-port {port} "
        f"--logfile {results_path}/worker_{worker_id}.log --loglevel {log_level}"
    )

    if target is not None:
        command += f" --host {target}"

    if headless:
        command += " --headless"

    if exclude_tags:
        command += f" --exclude-tags {' '.join(exclude_tags)}"

    return command


@dataclass
class ContextData:
    workers: list[subprocess.Popen] = field(default_factory=list)
    master: subprocess.Popen | None = None
    notifier: Notifier = field(default_factory=NoopNotifier)
