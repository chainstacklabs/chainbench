from chainbench.test_data import Account, BlockHash, BlockNumber, EvmTestData, TxHash
from chainbench.util.rng import RNG

from .http import JsonRpcUser


class EvmUser(JsonRpcUser):
    abstract = True
    test_data = EvmTestData()

    _default_trace_timeout = "120s"

    def _get_logs_params_factory(self, rng: RNG) -> list[dict]:
        block_range = self.test_data.get_random_block_range(20, rng)
        return [
            {
                "fromBlock": hex(block_range.start),
                "toBlock": hex(block_range.end),
            }
        ]

    def _transaction_by_hash_params_factory(self, rng: RNG) -> list[TxHash]:
        return [self.test_data.get_random_tx_hash(rng)]

    def _random_block_number_params_factory(self, rng: RNG) -> list[str]:
        return [hex(self.test_data.get_random_block_number(rng))]

    @staticmethod
    def _block_params_factory() -> list[str | bool]:
        return ["latest", True]

    def _block_by_hash_params_factory(self, rng: RNG) -> list[str | bool]:
        return [self.test_data.get_random_block_hash(rng), True]

    def _get_account_and_block_number_params_factory_latest(self, rng: RNG) -> list[Account | str]:
        return [self.test_data.get_random_account(rng), "latest"]

    def _get_balance_params_factory(self, rng: RNG) -> list[Account | str]:
        return [
            self.test_data.get_random_account(rng),
            "latest",
        ]

    def _debug_trace_call_params_factory(self, rng: RNG) -> list[dict | BlockNumber]:
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

    def _debug_trace_block_by_number_params_factory(self) -> list[str | dict]:
        return [
            "latest",
            {"tracer": "callTracer", "timeout": self._default_trace_timeout},
        ]

    def _debug_trace_block_by_hash_params_factory(self, rng: RNG) -> list[BlockHash | dict]:
        return [
            self.test_data.get_random_block_hash(rng),
            {"tracer": "callTracer", "timeout": self._default_trace_timeout},
        ]

    @staticmethod
    def _trace_replay_block_transaction_params_factory() -> list[str | list[str]]:
        return [
            "latest",
            ["vmTrace", "trace", "stateDiff"],
        ]

    def _trace_replay_transaction_params_factory(self, rng: RNG) -> list[TxHash | list[str]]:
        return [
            self.test_data.get_random_tx_hash(rng),
            ["vmTrace", "trace", "stateDiff"],
        ]

    def _debug_trace_transaction_params_factory(self, rng: RNG) -> list[TxHash | dict]:
        return [
            self.test_data.get_random_tx_hash(rng),
            {"tracer": "callTracer", "timeout": self._default_trace_timeout},
        ]

    def _trace_filter_params_factory(self, rng: RNG) -> list[dict]:
        block_number = self.test_data.get_random_block_number(rng)
        return [
            {
                "fromAddress": [self.test_data.get_random_account(rng)],
                "fromBlock": hex(block_number),
                "toBlock": hex(block_number + rng.random.randint(0, 20)),
            }
        ]

    @staticmethod
    def _eth_fee_history_params_factory(rng: RNG) -> list[int | str | list[int]]:
        return [rng.random.randint(1, 1024), "latest", [25, 75]]

    def _erc20_eth_call_params_factory(self, rng: RNG):
        contract = self.test_data.get_random_erc20_contract(rng)
        functions_params = [
            contract.total_supply_params(),
            contract.balance_of_params(self.test_data.get_random_account(rng)),
            contract.symbol_params(),
            contract.name_params(),
        ]
        return [
            rng.random.choice(functions_params),
            "latest",
        ]

    def _erc20_eth_get_code_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_erc20_contract(rng).address,
            "latest",
        ]
