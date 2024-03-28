"""
EVM profile (light mode).
"""

from locust import constant_pacing, task

from chainbench.user import EvmUser
from chainbench.util.rng import get_rng


class EvmLightProfile(EvmUser):
    wait_time = constant_pacing(1)

    @task
    def get_transaction_receipt_task(self):
        self.make_rpc_call(
            name="get_transaction_receipt",
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task
    def block_number_task(self):
        self.make_rpc_call(
            name="block_number",
            method="eth_blockNumber",
        ),

    @task
    def get_balance_task(self):
        self.make_rpc_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_account_and_block_number_params_factory_latest(get_rng()),
        ),

    @task
    def chain_id_task(self):
        self.make_rpc_call(
            name="chain_id",
            method="eth_chainId",
        ),

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_rpc_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task
    def client_version_task(self):
        self.make_rpc_call(
            name="client_version",
            method="web3_clientVersion",
        ),
