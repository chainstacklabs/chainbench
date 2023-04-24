"""
Polygon profile.

Note, that eth_sendRawTransaction is excluded from the test because it requires
building a transaction and signing it.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "eth_call" : 100
    "eth_getTransactionReceipt" : 64
    "eth_chainId" : 20
    "eth_getBlockByNumber" : 17
    "eth_blockNumber" : 16
    "eth_getTransactionByHash" : 11
    "eth_getLogs" : 11
    "Others" : 9
```
"""
from locust import task

from chainbench.user.evm import EVMBenchUser


class PolygonProfile(EVMBenchUser):
    @task(100)
    def call_task(self):
        self.make_call(
            name="call",
            method="eth_call",
            params=[
                {
                    "to": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                    "data": "0x70a08231000000000000000000000000F977814e90dA44bFA03b6295A0616a897441aceC",  # noqa: E501
                },
                "latest",
            ],
        ),

    @task(64)
    def get_transaction_receipt_task(self):
        self.make_call(
            name="get_transaction_receipt",
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task(20)
    def chain_id_task(self):
        self.make_call(
            name="chain_id",
            method="eth_chainId",
            params=[],
        ),

    @task(17)
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),

    @task(16)
    def block_number_task(self):
        self.make_call(
            name="block_number",
            method="eth_blockNumber",
            params=[],
        ),

    @task(11)
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task(11)
    def get_logs_task(self):
        self.make_call(
            name="get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(),
        ),

    @task(4)
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory_latest(),
        ),

    # TODO: introduce tags to make it possible to filter out unsupported methods
    # @task(2)
    def block_task(self):
        self.make_call(
            name="block",
            method="trace_block",
            params=self._block_by_number_params_factory(),
        ),
