# """
# EVM profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user.common import get_subclass_methods
from chainbench.user.protocol.evm import EvmRpcMethods, EvmUser


class EvmAllProfile(EvmUser):
    wait_time = constant_pacing(1)
    rpc_calls = {EvmUser.method_to_rpc_call(method): 1 for method in get_subclass_methods(EvmRpcMethods)}
    tasks = EvmUser.expand_tasks(rpc_calls)
