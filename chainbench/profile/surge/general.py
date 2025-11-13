from chainbench.user import EvmUser
from chainbench.util.rng import get_rng
from locust import task, constant_pacing


class SurgeProfile(EvmUser):
    wait_time = constant_pacing(2)

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="eth_getBlockByNumber",
            method="eth_getBlockByNumber",
            params=["0xa", True],
        ),

    @task
    def get_balance_task(self):
        self.make_rpc_call(
            name="eth_getBalance",
            method="eth_getBalance",
            params=[self.test_data.get_random_account(get_rng()), "latest"],
        ),
    
    @task
    def get_transaction_receipt_task(self):
        self.make_rpc_call(
            name="eth_getTransactionReceipt",
            method="eth_getTransactionReceipt",
            params=[self.test_data.get_random_tx_hash(get_rng())],
        ),
    
    @task
    def get_storage_at_task(self):
        self.make_rpc_call(
            name="eth_getStorageAt",
            method="eth_getStorageAt",
            params=[self.test_data.get_random_account(get_rng()), "0x0", "latest"],
        ),
