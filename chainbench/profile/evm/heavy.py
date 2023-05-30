"""
Ethereum profile (heavy mode).
"""
from locust import constant_pacing, tag, task

from chainbench.user.evm import EVMBenchUser


class EthereumHeavyProfile(EVMBenchUser):
    wait_time = constant_pacing(10)

    @task
    def trace_transaction_task(self):
        self.make_call(
            name="trace_transaction",
            method="debug_traceTransaction",
            params=[],
        ),

    @task
    def block_task(self):
        self.make_call(
            name="block",
            method="trace_block",
            params=self._block_by_number_params_factory(),
        ),

    @tag("getLogs")
    @task
    def get_logs_task(self):
        self.make_call(
            name="get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(),
        ),
