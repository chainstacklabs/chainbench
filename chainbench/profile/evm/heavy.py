"""
EVM profile (heavy mode).
"""

from random import randint

from locust import constant_pacing, tag, task

from chainbench.user import EvmUser
from chainbench.util.rng import get_rng


class EvmHeavyProfile(EvmUser):
    wait_time = constant_pacing(10)

    @task
    def debug_trace_transaction_task(self):
        self.make_rpc_call(
            name="debug_trace_transaction",
            method="debug_traceTransaction",
            params=self._debug_trace_transaction_params_factory(get_rng()),
        ),

    @task
    def trace_block_task(self):
        self.make_rpc_call(
            name="trace_block",
            method="trace_block",
            params=self._block_params_factory(),
        ),

    @tag("get-logs")
    @task
    def eth_get_logs_task(self):
        self.make_rpc_call(
            name="eth_get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(get_rng()),
        ),

    @task
    def eth_get_blocks_receipts_task(self):
        self.make_rpc_call(
            name="eth_get_block_receipts",
            method="eth_getBlockReceipts",
            params=[hex(self.test_data.get_random_block_number(get_rng()))],
        )

    @task
    def trace_replay_transaction_task(self):
        self.make_rpc_call(
            name="trace_replay_transaction",
            method="trace_replayTransaction",
            params=self._trace_replay_transaction_params_factory(get_rng()),
        )

    @task
    def trace_replay_block_transactions_task(self):
        self.make_rpc_call(
            name="trace_replay_block_transactions",
            method="trace_replayBlockTransactions",
            params=self._trace_replay_block_transaction_params_factory(),
        )

    @task
    def trace_call_task(self):
        self.make_rpc_call(
            name="trace_call",
            method="trace_call",
            params=[
                {
                    "to": "0x6b175474e89094c44da98b954eedeac495271d0f",
                    "data": "0x70a082310000000000000000000000006E0d01A76C3Cf4288372a29124A26D4353EE51BE",  # noqa E501
                },
                ["trace"],
                "latest",
            ],
        )

    @task
    def trace_filter_task(self):
        self.make_rpc_call(
            name="trace_filter",
            method="trace_filter",
            params=self._trace_filter_params_factory(get_rng()),
        )

    @task
    def debug_trace_call_task(self):
        self.make_rpc_call(
            name="debug_trace_call",
            method="debug_traceCall",
            params=[
                {
                    "data": "0xd0e30db0",
                    "from": "0x035C9c507149Fa30b17F9735BF97B4642C73464f",
                    "gas": "0x1E9EF",
                    "gasPrice": "0xBD32B2ABC",
                    "to": "0x0000000000a39bb272e79075ade125fd351887ac",
                },
                "latest",
                {"tracer": "callTracer"},
            ],
        )

    @task
    def debug_storage_range_at_task(self):
        self.make_rpc_call(
            name="debug_storage_range_at",
            method="debug_storageRangeAt",
            params=[
                "0x99136e1fd072ff630537cf7231c355a6839d848f7673026a7b100a92b26c9f4b",
                0,
                "0x27C70Cd1946795B66be9d954418546998b546634",
                "0x0000000000000000000000000000000000000000000000000000000000000000",
                randint(1000, 10000),
            ],
        )

    @task
    def debug_trace_block_by_number_task(self):
        self.make_rpc_call(
            name="debug_trace_block_by_number",
            method="debug_traceBlockByNumber",
            params=self._debug_trace_block_by_number_params_factory(),
        )

    @task
    def debug_trace_block_by_hash_task(self):
        self.make_rpc_call(
            name="debug_trace_block_by_hash",
            method="debug_traceBlockByHash",
            params=self._debug_trace_block_by_hash_params_factory(get_rng()),
        )

    @task
    def eth_estimate_gas_task(self):
        self.make_rpc_call(
            name="eth_estimate_gas",
            method="eth_estimateGas",
            params=self._erc20_eth_call_params_factory(get_rng()),
        )
