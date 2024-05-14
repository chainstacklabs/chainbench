"""
EVM eth_getLogs profile.
"""

from locust import constant_pacing

from chainbench.user import EvmUser


class EvmGetLogsProfile(EvmUser):
    wait_time = constant_pacing(10)

    rpc_calls = {
        EvmUser.eth_get_logs: 1,
    }

    tasks = EvmUser.expand_tasks(rpc_calls)
