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


class EvmMethods(EvmUser):
    abstract = True

    def eth_accounts_task(self) -> None:
        self.make_rpc_call(
            method="eth_accounts",
        )

    def eth_block_number_task(self) -> None:
        self.make_rpc_call(
            method="eth_blockNumber",
        )

    def eth_call_task(self):
        self.make_rpc_call(
            method="eth_call",
            params=self._erc20_eth_call_params_factory(self.rng.get_rng()),
        )

    def eth_chain_id_task(self):
        self.make_rpc_call(
            method="eth_chainId",
        )

    def eth_estimate_gas_task(self):
        self.make_rpc_call(
            name="eth_estimate_gas",
            method="eth_estimateGas",
            params=self._erc20_eth_call_params_factory(self.rng.get_rng()),
        )

    def eth_fee_history_task(self) -> None:
        self.make_rpc_call(
            method="eth_feeHistory",
            params=self._eth_fee_history_params_factory(self.rng.get_rng()),
        )

    def eth_gas_price_task(self) -> None:
        self.make_rpc_call(
            method="eth_gasPrice",
        )

    def eth_get_logs_task(self) -> None:
        self.make_rpc_call(
            method="eth_getLogs",
            params=self._get_logs_params_factory(self.rng.get_rng()),
        )

    def eth_get_balance_task(self) -> None:
        self.make_rpc_call(
            method="eth_getBalance",
            params=self._get_account_and_block_number_params_factory_latest(self.rng.get_rng()),
        )

    def eth_get_block_by_hash_task(self) -> None:
        self.make_rpc_call(
            method="eth_getBlockByHash",
            params=self._block_by_hash_params_factory(self.rng.get_rng()),
        )

    def eth_get_block_by_number_task(self) -> None:
        self.make_rpc_call(
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        )

    def eth_get_block_receipts_task(self) -> None:
        self.make_rpc_call(
            method="eth_getBlockReceipts",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    def eth_get_block_transaction_count_by_hash_task(self) -> None:
        self.make_rpc_call(
            method="eth_getBlockTransactionCountByHash",
            params=[self.test_data.get_random_block_hash(self.rng.get_rng())],
        )

    def eth_get_block_transaction_count_by_number_task(self) -> None:
        self.make_rpc_call(
            method="eth_getBlockTransactionCountByNumber",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    def eth_get_code_task(self) -> None:
        self.make_rpc_call(
            method="eth_getCode",
            params=self._erc20_eth_get_code_params_factory(self.rng.get_rng()),
        )

    def eth_get_header_by_hash_task(self) -> None:
        self.make_rpc_call(
            method="eth_getHeaderByHash",
            params=[self.test_data.get_random_block_hash(self.rng.get_rng())],
        )

    def eth_get_header_by_number_task(self) -> None:
        self.make_rpc_call(
            method="eth_getHeaderByNumber",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    def eth_get_transaction_by_hash_task(self) -> None:
        self.make_rpc_call(
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(self.rng.get_rng()),
        )

    def eth_get_transaction_receipt_task(self) -> None:
        self.make_rpc_call(
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(self.rng.get_rng()),
        )

    def eth_get_transaction_by_block_hash_and_index_task(self) -> None:
        self.make_rpc_call(
            method="eth_getTransactionByBlockHashAndIndex",
            params=[
                self.test_data.get_random_block_hash(self.rng.get_rng()),
                hex(self.rng.get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_by_block_number_and_index_task(self) -> None:
        self.make_rpc_call(
            method="eth_getTransactionByBlockNumberAndIndex",
            params=[
                hex(self.test_data.get_random_block_number(self.rng.get_rng())),
                hex(self.rng.get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_count_task(self) -> None:
        self.make_rpc_call(
            method="eth_getTransactionCount",
            params=self._get_account_and_block_number_params_factory_latest(self.rng.get_rng()),
        )

    def eth_get_uncle_count_by_block_hash_task(self) -> None:
        self.make_rpc_call(
            method="eth_getUncleCountByBlockHash",
            params=[self.test_data.get_random_block_hash(self.rng.get_rng())],
        )

    def eth_get_uncle_count_by_block_number_task(self) -> None:
        self.make_rpc_call(
            method="eth_getUncleCountByBlockNumber",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    def eth_max_priority_fee_per_gas_task(self) -> None:
        self.make_rpc_call(
            method="eth_maxPriorityFeePerGas",
        )

    def eth_syncing_task(self) -> None:
        self.make_rpc_call(
            method="eth_syncing",
        )

    def debug_trace_block_by_hash_task(self) -> None:
        self.make_rpc_call(
            method="debug_traceBlockByHash",
            params=self._debug_trace_block_by_hash_params_factory(self.rng.get_rng()),
        )

    def debug_trace_block_by_number_task(self) -> None:
        self.make_rpc_call(
            method="debug_traceBlockByNumber",
            params=self._debug_trace_block_by_number_params_factory(),
        )

    def debug_trace_call_task(self) -> None:
        self.make_rpc_call(
            method="debug_traceCall",
            params=self._debug_trace_call_params_factory(self.rng.get_rng()),
        )

    def debug_trace_transaction_task(self) -> None:
        self.make_rpc_call(
            method="debug_traceTransaction",
            params=self._debug_trace_transaction_params_factory(self.rng.get_rng()),
        )

    def net_listening_task(self) -> None:
        self.make_rpc_call(
            method="net_listening",
        )

    def net_peer_count_task(self) -> None:
        self.make_rpc_call(
            method="net_peerCount",
        )

    def net_version_task(self) -> None:
        self.make_rpc_call(
            method="net_version",
        )

    def trace_block_task(self) -> None:
        self.make_rpc_call(
            method="trace_block",
            params=self._block_params_factory(),
        )

    def trace_replay_block_transactions_task(self) -> None:
        self.make_rpc_call(
            method="trace_replayBlockTransactions",
            params=self._trace_replay_block_transaction_params_factory(),
        )

    def trace_replay_transaction_task(self) -> None:
        self.make_rpc_call(
            method="trace_replayTransaction",
            params=self._trace_replay_transaction_params_factory(self.rng.get_rng()),
        )

    def trace_transaction_task(self) -> None:
        self.make_rpc_call(
            method="trace_transaction",
            params=[self.test_data.get_random_tx_hash(self.rng.get_rng())],
        )

    def web3_client_version_task(self) -> None:
        self.make_rpc_call(
            method="web3_clientVersion",
        )

    def web3_sha3_task(self) -> None:
        self.make_rpc_call(
            method="web3_sha3",
            params=[self.test_data.get_random_tx_hash(self.rng.get_rng())],
        )
