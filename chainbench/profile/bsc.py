"""
Bsc profile.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "eth_call" : 100
    "eth_getTransactionReceipt" : 93
    "eth_getLogs" : 36
    "eth_blockNumber" : 28
    "eth_chainId" : 18
    "eth_getBlockByNumber" : 13
    "Others" : 20
```
"""
from locust import task

from chainbench.user.evm import EVMBenchUser


class BscProfile(EVMBenchUser):
    @task(100)
    def call_task(self):
        self.make_call(
            name="call",
            method="eth_call",
            params=[
                {
                    "to": "0x55d398326f99059fF775485246999027B3197955",
                    "data": "0x70a08231000000000000000000000000f977814e90da44bfa03b6295a0616a897441acec",  # noqa: E501
                },
                "latest",
            ],
        ),

    @task(93)
    def get_transaction_receipt_task(self):
        self.make_call(
            name="get_transaction_receipt",
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task(36)
    def get_logs_task(self):
        self.make_call(
            name="get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(),
        ),

    @task(28)
    def block_number_task(self):
        self.make_call(
            name="block_number",
            method="eth_blockNumber",
            params=[],
        ),

    @task(18)
    def chain_id_task(self):
        self.make_call(
            name="chain_id",
            method="eth_chainId",
            params=[],
        ),

    @task(13)
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),

    @task(9)
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task(5)
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory_latest(),
        ),

    @task(3)
    def get_block_by_hash_task(self):
        self.make_call(
            name="get_block_by_hash",
            method="eth_getBlockByHash",
            params=self._block_by_hash_params_factory(),
        ),
