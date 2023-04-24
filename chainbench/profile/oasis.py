from locust import between, task

from chainbench.user.evm import EVMBenchUser


class OasisProfile(EVMBenchUser):
    wait_time = between(0.1, 1.5)

    @task
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),

    @task
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_transaction_count_task(self):
        self.make_call(
            name="get_transaction_count",
            method="eth_getTransactionCount",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_code_task(self):
        self.make_call(
            name="get_code",
            method="eth_getCode",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task
    def get_block_number_task(self):
        self.make_call(
            name="block_number",
            method="eth_blockNumber",
        ),

    @task
    def get_syncing_task(self):
        self.make_call(
            name="get_syncing",
            method="eth_syncing",
        ),

    @task
    def get_block_transaction_count_by_number_task(self):
        self.make_call(
            name="get_block_transaction_count_by_number",
            method="eth_getBlockTransactionCountByNumber",
            params=self._random_block_number_params_factory(),
        ),
