import random

from chainbench.test_data import EVMTestData
from chainbench.user.base import BaseBenchUser
from chainbench.util.rng import RNG


class EVMBenchUser(BaseBenchUser):
    abstract = True
    test_data = EVMTestData()

    _default_trace_timeout = "120s"

    def _get_logs_params_factory(self, rng: RNG):
        return [
            {
                "fromBlock": hex(self.test_data.get_random_recent_block_number(20, rng)),
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

    def _trace_call_params_factory(self, rng: RNG):
        tx_data = self.test_data.get_random_tx(rng)
        tx_param = {
            "to": tx_data["to"],
            "gas": tx_data["gas"],
            "value": tx_data["value"],
        }

        if "maxFeePerGas" in tx_data:
            tx_param["maxFeePerGas"] = tx_data["maxFeePerGas"]
        else:
            tx_param["gasPrice"] = tx_data["gasPrice"]

        if "input" in tx_data:
            if tx_data["input"] != "0x":
                tx_param["data"] = tx_data["input"]

        if "accessList" in tx_data:
            if len(tx_data["accessList"]) > 0:
                tx_param["accessList"] = tx_data["accessList"]

        return [
            tx_param,
            tx_data["blockNumber"],
            {"tracer": "callTracer", "timeout": self._default_trace_timeout},
        ]

    def _trace_block_by_number_params_factory(self, rng: RNG):
        return [
            hex(self.test_data.get_random_block_number(rng)),
            {"tracer": "callTracer", "timeout": self._default_trace_timeout},
        ]

    def _trace_block_by_hash_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_block_hash(rng),
            {"tracer": "callTracer", "timeout": self._default_trace_timeout},
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
        return [
            self.test_data.get_random_tx_hash(rng),
            {"tracer": "callTracer", "timeout": self._default_trace_timeout},
        ]

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
