import random

from chainbench.test_data import EVMTestData
from chainbench.user.base import BaseBenchUser


def random_bool():
    return random.choice([True, False])


class EVMBenchUser(BaseBenchUser):
    abstract = True
    test_data = EVMTestData()

    def _get_logs_params_factory(self):
        return [
            {
                "fromBlock": self.test_data.get_random_recent_block_number_hex(20),
                "toBlock": "latest",
            }
        ]

    def _transaction_by_hash_params_factory(self):
        return [self.test_data.get_random_tx_hash()]

    def _random_block_number_params_factory(self):
        return [self.test_data.get_random_block_number_hex()]

    def _block_by_number_params_factory(self):
        return [self.test_data.get_random_block_number_hex(), random_bool()]

    def _block_by_hash_params_factory(self):
        return [self.test_data.get_random_block_hash(), random_bool()]

    def _get_balance_params_factory_latest(self):
        return [self.test_data.get_random_account(), "latest"]

    def _get_balance_params_factory(self):
        return [
            self.test_data.get_random_account(),
            self.test_data.get_random_block_number_hex(),
        ]
