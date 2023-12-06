"""
Ethereum profile (heavy mode).
"""

from locust import constant_pacing, task

from chainbench.user.evm import EVMBenchUser
from chainbench.util.rng import get_rng


class EthereumDebugTraceProfile(EVMBenchUser):
    wait_time = constant_pacing(10)

    @task(324)
    def debug_trace_transaction_task(self):
        self.make_call(
            name="debug_trace_transaction",
            method="debug_traceTransaction",
            params=self._trace_transaction_params_factory(get_rng()),
        ),

    @task(41)
    def debug_trace_call_task(self):
        self.make_call(
            name="debug_trace_call",
            method="debug_traceCall",
            params=self._trace_call_params_factory(get_rng()),
        ),

    @task(36)
    def debug_trace_block_by_number_task(self):
        self.make_call(
            name="debug_trace_block_by_number",
            method="debug_traceBlockByNumber",
            params=self._trace_block_by_number_params_factory(get_rng()),
        ),

    @task(1)
    def debug_trace_block_by_hash_task(self):
        self.make_call(
            name="debug_trace_block_by_hash",
            method="debug_traceBlockByHash",
            params=self._trace_block_by_hash_params_factory(get_rng()),
        ),
