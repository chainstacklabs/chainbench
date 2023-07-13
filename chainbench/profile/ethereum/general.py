"""
Ethereum profile.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "eth_call" : 100
    "eth_getTransactionReceipt" : 24
    "eth_blockNumber" : 19
    "eth_getBalance" : 12
    "eth_chainId" : 11
    "eth_getBlockByNumber" : 9
    "eth_getTransactionByHash" : 8
    "Others" : 12
```
"""
from locust import constant_pacing, tag, task

from chainbench.user.evm import EVMBenchUser
from chainbench.util.rng import get_rng


class EthereumProfile(EVMBenchUser):
    wait_time = constant_pacing(2)
    weight = 487

    @task(100)
    def call_task(self):
        self.make_call(
            name="call",
            method="eth_call",
            params=[
                {
                    "to": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    "data": "0x70a082310000000000000000000000009696f59E4d72E237BE84fFD425DCaD154Bf96976",  # noqa: E501
                },
                "latest",
            ],
        ),

    @task(24)
    def get_transaction_receipt_task(self):
        self.make_call(
            name="get_transaction_receipt",
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task(19)
    def block_number_task(self):
        self.make_call(
            name="block_number",
            method="eth_blockNumber",
            params=[],
        ),

    @task(12)
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory_latest(get_rng()),
        ),

    @task(11)
    def chain_id_task(self):
        self.make_call(
            name="chain_id",
            method="eth_chainId",
            params=[],
        ),

    @task(9)
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(get_rng()),
        ),

    @task(8)
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @tag("debug")
    @task(3)
    def trace_transaction_task(self):
        self.make_call(
            name="trace_transaction",
            method="debug_traceTransaction",
            params=[],
        ),

    @task(2)
    def client_version_task(self):
        self.make_call(
            name="client_version",
            method="web3_clientVersion",
            params=[],
        ),


class GetLogsProfile(EVMBenchUser):
    wait_time = constant_pacing(10)
    weight = 13

    @tag("get-logs")
    @task
    def get_logs_task(self):
        self.make_call(
            name="get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(get_rng()),
        ),
