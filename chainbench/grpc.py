"""``chainbench grpc`` — Solana Yellowstone gRPC benchmarks.

Thin pass-through to the ``chainbench-grpc`` Rust binary (shipped on ``PATH`` in
the ChainBench Docker image). It forwards stdout/stderr and the process exit
code; the binary owns its own flags, validation, and ``--help``. Pass tool flags
after the mode, e.g.::

    chainbench grpc latency --url https://grpc.example.com --token TOKEN
    chainbench grpc race -u https://a -t t1 -u https://b -t t2 --transactions 5000
    chainbench grpc latency --help   # rendered by the binary
"""

import shutil
import subprocess
import sys

import click

GRPC_BIN = "chainbench-grpc"
GRPC_REPO = "https://github.com/chainstacklabs/chainbench-grpc"
MODES = ("race", "latency", "throughput", "slots", "full")


def _run(mode: str, args: tuple[str, ...]) -> None:
    exe = shutil.which(GRPC_BIN)
    if exe is None:
        raise click.ClickException(
            f"`{GRPC_BIN}` not found on PATH. It ships in the ChainBench Docker "
            f"image; for local use install it from {GRPC_REPO}"
        )
    completed = subprocess.run([exe, mode, *args])
    sys.exit(completed.returncode)


@click.group(
    name="grpc",
    help=(
        "Solana Yellowstone gRPC benchmarks (delegates to the chainbench-grpc "
        "binary). Flags after the mode are passed through to the binary, e.g. "
        "`grpc latency --url URL --token TOKEN`."
    ),
)
def grpc() -> None:
    pass


def _register(mode: str) -> None:
    @grpc.command(
        name=mode,
        help=f"Run chainbench-grpc `{mode}` (flags are passed through to the binary).",
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
        add_help_option=False,  # let the binary render its own --help
    )
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    def _cmd(args: tuple[str, ...]) -> None:
        _run(mode, args)


for _mode in MODES:
    _register(_mode)
