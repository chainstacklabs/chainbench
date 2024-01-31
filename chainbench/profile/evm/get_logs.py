"""
EVM eth_getLogs profile.
"""

from locust import constant_pacing, task

from chainbench.user import EvmUser
from chainbench.util.rng import get_rng


class EvmGetLogsProfile(EvmUser):
    wait_time = constant_pacing(10)

    @task
    def get_logs_task(self):
        self.make_rpc_call(
            name="get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(get_rng()),
        ),
