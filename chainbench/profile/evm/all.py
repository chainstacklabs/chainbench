# """
# EVM profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user.evm import EVMMethods
from chainbench.util.cli import get_subclass_methods


class EVMAllProfile(EVMMethods):
    wait_time = constant_pacing(1)
    tasks = [EVMMethods.get_method(method) for method in get_subclass_methods(EVMMethods)]
