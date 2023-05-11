"""
Ethereum profile (light mode).
"""
from locust import task

from chainbench.user.evm import EVMBenchUser


class EthereumLightProfile(EVMBenchUser):
    @task
    def get_transaction_receipt_task(self):
        self.make_call(
            name="get_transaction_receipt",
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task
    def block_number_task(self):
        self.make_call(
            name="block_number",
            method="eth_blockNumber",
            params=[],
        ),

    @task
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory_latest(),
        ),

    @task
    def chain_id_task(self):
        self.make_call(
            name="chain_id",
            method="eth_chainId",
            params=[],
        ),

    @task
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task
    def client_version_task(self):
        self.make_call(
            name="client_version",
            method="web3_clientVersion",
            params=[],
        ),
