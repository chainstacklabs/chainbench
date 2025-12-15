from chainbench.user import EvmUser
from locust import constant_pacing, task


class SurgeProfile(EvmUser):
    wait_time = constant_pacing(1)

    @task(35)
    def eth_call_task(self):
        self.make_rpc_call(
            name="eth_call",
            method="eth_call",
            params=[{"to": "0xE837861567a541EFbcf0a8A6C56aEb61dD7A2C20", "data": "0x20965255"}, "latest"],
        )

    @task(15)
    def get_logs_task(self):
        self.make_rpc_call(
            name="eth_getLogs",
            method="eth_getLogs",
            params=self._get_logs_params_factory(self.rng.get_rng()),
        )

    @task(5)
    def estimate_gas_task(self):
        self.make_rpc_call(
            name="eth_estimateGas",
            method="eth_estimateGas",
            params=[{"to": "0xE837861567a541EFbcf0a8A6C56aEb61dD7A2C20", "data": "0x20965255"}],
        )

    @task(10)
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="eth_getBlockByNumber",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        )

    @task(8)
    def get_balance_task(self):
        self.make_rpc_call(
            name="eth_getBalance",
            method="eth_getBalance",
            params=["0x0742D35Cc6634c0532925A3b844bc9e7595f3574", "latest"],
        )

    @task(7)
    def get_transaction_receipt_task(self):
        self.make_rpc_call(
            name="eth_getTransactionReceipt",
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(self.rng.get_rng()),
        )

    @task(5)
    def get_storage_at_task(self):
        self.make_rpc_call(
            name="eth_getStorageAt",
            method="eth_getStorageAt",
            params=["0x0742D35Cc6634c0532925A3b844bc9e7595f3574", "0x0", "latest"],
        )

    @task(5)
    def get_gas_price_task(self):
        self.make_rpc_call(
            name="eth_gasPrice",
            method="eth_gasPrice",
            params=[],
        )

    @task(2)
    def get_chain_id_task(self):
        self.make_rpc_call(
            name="eth_chainId",
            method="eth_chainId",
            params=[],
        )

    @task(1)
    def net_version_task(self):
        self.make_rpc_call(
            name="net_version",
            method="net_version",
            params=[],
        )

    @task(1)
    def syncing_task(self):
        self.make_rpc_call(
            name="eth_syncing",
            method="eth_syncing",
            params=[],
        )

    @task(1)
    def get_max_priority_fee_per_gas_task(self):
        self.make_rpc_call(
            name="eth_maxPriorityFeePerGas",
            method="eth_maxPriorityFeePerGas",
            params=[],
        )

    @task(2)
    def get_fee_history_task(self):
        self.make_rpc_call(
            name="eth_feeHistory",
            method="eth_feeHistory",
            params=["0x5", "latest", [50, 90]],
        )

    @task(1)
    def get_block_number_task(self):
        self.make_rpc_call(
            name="eth_blockNumber",
            method="eth_blockNumber",
            params=[],
        )

    @task(1)
    def get_block_receipts_task(self):
        self.make_rpc_call(
            name="eth_getBlockReceipts",
            method="eth_getBlockReceipts",
            params=["latest"],
        )

    @task(1)
    def get_block_transaction_count_by_number_task(self):
        self.make_rpc_call(
            name="eth_getBlockTransactionCountByNumber",
            method="eth_getBlockTransactionCountByNumber",
            params=["latest"],
        )