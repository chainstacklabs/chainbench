# """
# Solana profile (all supported methods).
# """

from locust import constant_pacing

from chainbench.user.common import get_subclass_methods
from chainbench.user.protocol.solana import SolanaRpcMethods, SolanaUser


class SolanaAllProfile(SolanaUser):
    wait_time = constant_pacing(1)
    rpc_calls = {SolanaUser.method_to_rpc_call(method): 1 for method in get_subclass_methods(SolanaRpcMethods)}
    tasks = SolanaUser.expand_tasks(rpc_calls)
