import random

from chainbench.test_data import EVMTestData
from chainbench.user.base import BaseBenchUser
from chainbench.util.rng import RNG


class EVMBenchUser(BaseBenchUser):
    abstract = True
    test_data = EVMTestData()

    def _get_logs_params_factory(self, rng: RNG):
        return [
            {
                "fromBlock": hex(
                    self.test_data.get_random_recent_block_number(20, rng)
                ),
                "toBlock": hex(self.test_data.end_block_number),
            }
        ]

    def _transaction_by_hash_params_factory(self, rng: RNG):
        return [self.test_data.get_random_tx_hash(rng)]

    def _random_block_number_params_factory(self, rng: RNG):
        return [hex(self.test_data.get_random_block_number(rng))]

    def _block_params_factory(self, rng: RNG):
        return [hex(self.test_data.get_random_block_number(rng)), True]

    def _block_by_hash_params_factory(self, rng: RNG):
        return [self.test_data.get_random_block_hash(rng), True]

    def _get_balance_params_factory_latest(self, rng: RNG):
        return [self.test_data.get_random_account(rng), "latest"]

    def _get_balance_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_account(rng),
            hex(self.test_data.get_random_block_number(rng)),
        ]

    def _trace_block_by_number_params_factory(self, rng: RNG):
        return [
            hex(self.test_data.get_random_block_number(rng)),
            {"tracer": "callTracer"},
        ]

    def _trace_block_by_hash_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_block_hash(rng),
            {"tracer": "callTracer"},
        ]

    def _trace_replay_block_transaction_params_factory(self, rng: RNG):
        return [
            hex(self.test_data.get_random_block_number(rng)),
            ["vmTrace", "trace", "stateDiff"],
        ]

    def _trace_replay_transaction_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_tx_hash(rng),
            ["vmTrace", "trace", "stateDiff"],
        ]

    def _trace_transaction_params_factory(self, rng: RNG):
        return [self.test_data.get_random_tx_hash(rng), {"tracer": "prestateTracer"}]

    def _trace_filter_params_factory(self, rng: RNG):
        block_number = self.test_data.get_random_block_number(rng)
        return [
            {
                "fromAddress": [self.test_data.get_random_account(rng)],
                "fromBlock": hex(block_number),
                "toBlock": hex(block_number + random.randint(0, 20)),
            }
        ]

    def _eth_estimate_gas_params_factory(self, rng: RNG):
        return [
            {
                "from": self.test_data.get_random_account(rng),
                "to": "0x18318221d811Da0fe45412394eAf2C42A10BC678",
            }
        ]
