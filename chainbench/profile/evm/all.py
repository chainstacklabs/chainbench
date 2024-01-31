# """
# EVM profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user import EvmMethods
from chainbench.util.cli import get_subclass_methods


class EvmAllProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = [EvmMethods.get_method(method) for method in get_subclass_methods(EvmMethods)]
