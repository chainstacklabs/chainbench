"""
Avalanche profile.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "eth_call" : 100
    "eth_getBlockByNumber" : 50
    "eth_getLogs" : 24
    "eth_getTransactionReceipt" : 17
    "eth_chainId" : 15
    "eth_blockNumber" : 15
    "eth_getBalance" : 11
    "Others" : 28
```
"""
from locust import constant_pacing, tag, task

from chainbench.user.evm import EVMBenchUser
from chainbench.util.rng import get_rng


class AvalancheProfile(EVMBenchUser):
    wait_time = constant_pacing(2)
    weight = 91

    @task(100)
    def call_task(self):
        self.make_call(
            name="call",
            method="eth_call",
            params=[
                {
                    "to": "0x7325e3564B89968D102B3261189EA44c0f5f1a8e",
                    "data": "0x18160ddd0000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
                "latest",
            ],
        ),

    @task(50)
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(get_rng()),
        ),

    @task(17)
    def get_transaction_receipt_task(self):
        self.make_call(
            name="get_transaction_receipt",
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task(15)
    def chain_id_task(self):
        self.make_call(
            name="chain_id",
            method="eth_chainId",
        ),

    @task(15)
    def block_number_task(self):
        self.make_call(
            name="block_number",
            method="eth_blockNumber",
        ),

    @task(11)
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory_latest(get_rng()),
        ),

    @task(10)
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task(5)
    def estimate_gas_task(self):
        self.make_call(
            name="estimate_gas",
            method="eth_estimateGas",
            params=[
                {
                    "from": "0x9f8c163cBA728e99993ABe7495F06c0A3c8Ac8b9",
                    "to": "0xC2DE4f542C2e2349ee050541F5AD25aa4BE1a00f",
                    "value": "0xde0b6b3a7640000",
                }
            ],
        ),

    @task(4)
    def client_version_task(self):
        self.make_call(
            name="client_version",
            method="web3_clientVersion",
        ),

    @task(3)
    def get_block_by_hash_task(self):
        self.make_call(
            name="get_block_by_hash",
            method="eth_getBlockByHash",
            params=self._block_by_hash_params_factory(get_rng()),
        ),

    @task(3)
    def gas_price_task(self):
        self.make_call(
            name="gas_price",
            method="eth_gasPrice",
        ),

    @task(3)
    def max_priority_fee_per_gas_task(self):
        self.make_call(
            name="max_priority_fee_per_gas",
            method="eth_maxPriorityFeePerGas",
        ),


class GetLogsProfile(EVMBenchUser):
    wait_time = constant_pacing(10)
    weight = 9

    @tag("get-logs")
    @task
    def get_logs_task(self):
        self.make_call(
            name="get_logs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(get_rng()),
        ),
