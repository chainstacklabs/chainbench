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
                "fromBlock": hex(
                    self.test_data.latest_block_number - random.randint(0, 20)
                ),
                "toBlock": hex(self.test_data.latest_block_number),
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

    def _trace_block_by_number_params_factory(self):
        return [
            self.test_data.get_random_block_number_hex(),
            {"tracer": "callTracer"},
        ]

    def _trace_block_by_hash_params_factory(self):
        return [
            self.test_data.get_random_block_hash(),
            {"tracer": "callTracer"},
        ]

    def _trace_replay_block_transaction_by_block_number_params_factory(self):
        return [
            self.test_data.get_random_block_number_hex(),
            ["vmTrace", "trace", "stateDiff"],
        ]

    def _trace_replay_transaction_by_hash_params_factory(self):
        return [self.test_data.get_random_tx_hash(), ["vmTrace", "trace", "stateDiff"]]

    def _trace_transaction_by_hash_params_factory(self):
        return [self.test_data.get_random_tx_hash(), {"tracer": "prestateTracer"}]

    def _trace_filter_params_factory(self):
        block_number = self.test_data.get_random_block_number()
        return [
            {
                "fromAddress": [self.test_data.get_random_account()],
                "fromBlock": hex(block_number),
                "toBlock": hex(block_number + random.randint(0, 20)),
            }
        ]

    def _eth_estimate_gas_params_factory(self):
        return [
            {
                "from": self.test_data.get_random_account(),
                "to": "0x18318221d811Da0fe45412394eAf2C42A10BC678",
            }
        ]
