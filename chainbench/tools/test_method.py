"""
User profile for testing a specific EVM method.
"""
from locust import constant_pacing, events, task
from locust.argument_parser import LocustArgumentParser

from chainbench.user import EvmMethods
from chainbench.util.cli import get_subclass_methods, method_to_task, task_to_method


@events.init_command_line_parser.add_listener
def _(parser: LocustArgumentParser) -> None:
    parser.add_argument(
        "--method",
        type=str,
        default="eth_blocknumber",
        choices=[task_to_method(method) for method in get_subclass_methods(EvmMethods)],
        help="Test a specific method",
        include_in_web_ui=True,
    )


class TestEVMMethod(EvmMethods):
    wait_time = constant_pacing(1)

    @task
    def run_task(self) -> None:
        self.get_method(method_to_task(self.environment.parsed_options.method))(self)
