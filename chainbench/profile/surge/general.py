from chainbench.user import EvmUser
from chainbench.util.rng import get_rng
from locust import task, constant_pacing


class SurgeProfile(EvmUser):
    wait_time = constant_pacing(2)

    @task
    def get_gas_price_task(self):
        self.make_rpc_call(
            name="eth_gasPrice",
            method="eth_gasPrice",
            params=[],
        ),

    @task
    def get_chain_id_task(self):
        self.make_rpc_call(
            name="eth_chainId",
            method="eth_chainId",
            params=[],
        ),

    @task
    def net_version_task(self):
        self.make_rpc_call(
            name="net_version",
            method="net_version",
            params=[],
        ),

    @task
    def syncing_task(self):
        self.make_rpc_call(
            name="eth_syncing",
            method="eth_syncing",
            params=[],
        ),
    
    @task
    def get_max_priority_fee_per_gas_task(self):
        self.make_rpc_call(
            name="eth_maxPriorityFeePerGas",
            method="eth_maxPriorityFeePerGas",
            params=[],
        ),

    @task
    def get_fee_history_task(self):
        self.make_rpc_call(
            name="eth_feeHistory",
            method="eth_feeHistory",
            params=["0x5", "latest", [50, 90]],
        ),

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="eth_getBlockByNumber",
            method="eth_getBlockByNumber",
            params=["latest", True],
        ),

    @task
    def get_balance_task(self):
        self.make_rpc_call(
            name="eth_getBalance",
            method="eth_getBalance",
            params=["0x0742D35Cc6634c0532925A3b844bc9e7595f3574", "latest"],
        ),
    
    @task
    def get_block_number_task(self):
        self.make_rpc_call(
            name="eth_blockNumber",
            method="eth_blockNumber",
            params=[],
        ),

    @task
    def get_block_receipts_task(self):
        self.make_rpc_call(
            name="eth_getBlockReceipts",
            method="eth_getBlockReceipts",
            params=["latest"],
        ),
    
    @task
    def get_block_transaction_count_by_number_task(self):
        self.make_rpc_call(
            name="eth_getBlockTransactionCountByNumber",
            method="eth_getBlockTransactionCountByNumber",
            params=["latest"],
        ),