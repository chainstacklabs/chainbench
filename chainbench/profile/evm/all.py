# """
# EVM profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user.methods import EvmMethods
from chainbench.user.methods.common import get_subclass_functions


class EvmAllProfile(EvmMethods):
    wait_time = constant_pacing(1)
    tasks = [task.method for task in get_subclass_functions(EvmMethods)]
