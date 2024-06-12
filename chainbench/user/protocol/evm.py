import re

from chainbench.test_data import (
    Account,
    BlockHash,
    BlockNumber,
    EvmTestData,
    Tx,
    TxHash,
)
from chainbench.user.http import JsonRpcUser, RpcCall
from chainbench.user.tag import tag
from chainbench.util.rng import RNG


class EvmBaseUser(JsonRpcUser):
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
            "value": "0x0",
        }

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

    def _get_random_tx_params(self, rng: RNG, k: int = 1) -> list[Tx]:
        return [self.test_data.get_random_tx(rng) for _ in range(k)]

    def _trace_call_params_factory(self, rng: RNG) -> list[dict | list | BlockNumber]:
        tx_data = self._get_random_tx_params(rng)[0]
        tx_param = {
            "from": tx_data["from"],
            "to": tx_data["to"],
            "value": tx_data["value"],
        }

        return [
            tx_param,
            ["trace"],
            tx_data["blockNumber"],
        ]

    def _trace_call_many_params_factory(self, rng: RNG) -> list[dict | list | str]:
        tx_datas = self._get_random_tx_params(rng)
        traces = [
            [
                {
                    "from": tx_data["from"],
                    "to": tx_data["to"],
                    "value": tx_data["value"],
                },
                ["trace"],
            ]
            for tx_data in tx_datas
        ]

        return [
            traces,
            "latest",
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


class EvmRpcMethods(EvmBaseUser):
    abstract = True

    def eth_accounts(self) -> RpcCall:
        return RpcCall(method="eth_accounts")

    def eth_block_number(self) -> RpcCall:
        return RpcCall(method="eth_blockNumber")

    def eth_call(self) -> RpcCall:
        return RpcCall(method="eth_call", params=self._erc20_eth_call_params_factory(self.rng.get_rng()))

    def eth_chain_id(self) -> RpcCall:
        return RpcCall(method="eth_chainId")

    def eth_estimate_gas(self) -> RpcCall:
        return RpcCall(method="eth_estimateGas", params=self._erc20_eth_call_params_factory(self.rng.get_rng()))

    def eth_fee_history(self) -> RpcCall:
        return RpcCall(method="eth_feeHistory", params=self._eth_fee_history_params_factory(self.rng.get_rng()))

    @staticmethod
    def eth_gas_price() -> RpcCall:
        return RpcCall(method="eth_gasPrice")

    def eth_get_logs(self) -> RpcCall:
        return RpcCall(method="eth_getLogs", params=self._get_logs_params_factory(self.rng.get_rng()))

    def eth_get_balance(self) -> RpcCall:
        return RpcCall(
            method="eth_getBalance", params=self._get_account_and_block_number_params_factory_latest(self.rng.get_rng())
        )

    def eth_get_block_by_hash(self) -> RpcCall:
        return RpcCall(method="eth_getBlockByHash", params=self._block_by_hash_params_factory(self.rng.get_rng()))

    def eth_get_block_by_number(self) -> RpcCall:
        return RpcCall(method="eth_getBlockByNumber", params=self._block_params_factory())

    def eth_get_block_receipts(self) -> RpcCall:
        return RpcCall(
            method="eth_getBlockReceipts", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def eth_get_block_transaction_count_by_hash(self) -> RpcCall:
        return RpcCall(
            method="eth_getBlockTransactionCountByHash",
            params=[self.test_data.get_random_block_hash(self.rng.get_rng())],
        )

    def eth_get_block_transaction_count_by_number(self) -> RpcCall:
        return RpcCall(
            method="eth_getBlockTransactionCountByNumber",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    def eth_get_code(self) -> RpcCall:
        return RpcCall(method="eth_getCode", params=self._erc20_eth_get_code_params_factory(self.rng.get_rng()))

    def eth_get_header_by_hash(self) -> RpcCall:
        return RpcCall(method="eth_getHeaderByHash", params=[self.test_data.get_random_block_hash(self.rng.get_rng())])

    def eth_get_header_by_number(self) -> RpcCall:
        return RpcCall(
            method="eth_getHeaderByNumber", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def eth_get_transaction_by_hash(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionByHash", params=self._transaction_by_hash_params_factory(self.rng.get_rng())
        )

    def eth_get_transaction_receipt(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionReceipt", params=self._transaction_by_hash_params_factory(self.rng.get_rng())
        )

    def eth_get_transaction_by_block_hash_and_index(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionByBlockHashAndIndex",
            params=[
                self.test_data.get_random_block_hash(self.rng.get_rng()),
                hex(self.rng.get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_by_block_number_and_index(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionByBlockNumberAndIndex",
            params=[
                hex(self.test_data.get_random_block_number(self.rng.get_rng())),
                hex(self.rng.get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_count(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionCount",
            params=self._get_account_and_block_number_params_factory_latest(self.rng.get_rng()),
        )

    def eth_get_uncle_count_by_block_hash(self) -> RpcCall:
        return RpcCall(
            method="eth_getUncleCountByBlockHash", params=[self.test_data.get_random_block_hash(self.rng.get_rng())]
        )

    def eth_get_uncle_count_by_block_number(self) -> RpcCall:
        return RpcCall(
            method="eth_getUncleCountByBlockNumber",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    @staticmethod
    def eth_max_priority_fee_per_gas() -> RpcCall:
        return RpcCall(method="eth_maxPriorityFeePerGas")

    @staticmethod
    def eth_syncing() -> RpcCall:
        return RpcCall(method="eth_syncing")

    # TODO: Implement tags for rpc methods as well to enable filtering for batch requests

    @staticmethod
    def debug_get_bad_blocks() -> RpcCall:
        return RpcCall(method="debug_getBadBlocks")

    def debug_get_raw_block_by_number(self) -> RpcCall:
        return RpcCall(
            method="debug_getRawBlock", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def debug_get_raw_header_by_number(self) -> RpcCall:
        return RpcCall(
            method="debug_getRawHeader", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def debug_get_raw_receipts(self) -> RpcCall:
        return RpcCall(
            method="debug_getRawReceipts", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def debug_get_raw_transaction_by_hash(self) -> RpcCall:
        return RpcCall(method="debug_getRawTransaction", params=[self.test_data.get_random_tx_hash(self.rng.get_rng())])

    def debug_trace_bad_block(self) -> RpcCall:
        return RpcCall(method="debug_traceBadBlock", params=[self.test_data.get_random_block_hash(self.rng.get_rng())])

    def debug_trace_block(self) -> RpcCall:
        return RpcCall(method="debug_traceBlock", params=self._block_params_factory())

    def debug_trace_block_by_hash(self) -> RpcCall:
        return RpcCall(
            method="debug_traceBlockByHash", params=self._debug_trace_block_by_hash_params_factory(self.rng.get_rng())
        )

    def debug_trace_block_by_number(self) -> RpcCall:
        return RpcCall(method="debug_traceBlockByNumber", params=self._debug_trace_block_by_number_params_factory())

    def debug_trace_call(self) -> RpcCall:
        return RpcCall(method="debug_traceCall", params=self._debug_trace_call_params_factory(self.rng.get_rng()))

    def debug_storage_range_at(self) -> RpcCall:
        return RpcCall(
            method="debug_storageRangeAt",
            params=[
                self.test_data.get_random_block_hash(self.rng.get_rng()),
                self.test_data.get_random_account(self.rng.get_rng()),
                hex(self.rng.get_rng().random.randint(0, 20)),
                hex(self.rng.get_rng().random.randint(0, 20)),
            ],
        )

    def debug_trace_transaction(self) -> RpcCall:
        return RpcCall(
            method="debug_traceTransaction", params=self._debug_trace_transaction_params_factory(self.rng.get_rng())
        )

    @staticmethod
    def net_listening() -> RpcCall:
        return RpcCall(method="net_listening")

    @staticmethod
    def net_peer_count() -> RpcCall:
        return RpcCall(method="net_peerCount")

    @staticmethod
    def net_version() -> RpcCall:
        return RpcCall(method="net_version")

    def trace_block(self) -> RpcCall:
        return RpcCall(method="trace_block", params=self._block_params_factory())

    def trace_call(self) -> RpcCall:
        return RpcCall(method="trace_call", params=self._trace_call_params_factory(self.rng.get_rng()))

    def trace_call_many(self) -> RpcCall:
        return RpcCall(method="trace_callMany", params=self._trace_call_many_params_factory(self.rng.get_rng()))

    def trace_filter(self) -> RpcCall:
        return RpcCall(method="trace_filter", params=self._trace_filter_params_factory(self.rng.get_rng()))

    def trace_replay_block_transactions(self) -> RpcCall:
        return RpcCall(
            method="trace_replayBlockTransactions", params=self._trace_replay_block_transaction_params_factory()
        )

    def trace_replay_transaction(self) -> RpcCall:
        return RpcCall(
            method="trace_replayTransaction", params=self._trace_replay_transaction_params_factory(self.rng.get_rng())
        )

    def trace_transaction(self) -> RpcCall:
        return RpcCall(method="trace_transaction", params=[self.test_data.get_random_tx_hash(self.rng.get_rng())])

    @staticmethod
    def web3_client_version() -> RpcCall:
        return RpcCall(method="web3_clientVersion")

    def web3_sha3(self) -> RpcCall:
        return RpcCall(method="web3_sha3", params=[self.test_data.get_random_tx_hash(self.rng.get_rng())])


class EvmUser(EvmRpcMethods):
    abstract = True

    @staticmethod
    def task_to_method(task_name: str) -> str:
        task_name_stripped = task_name.replace("_task", "")
        words = task_name_stripped.split("_")
        namespace = words[0]
        method = "".join([words[1]] + [word.capitalize() for word in words[2:]])
        return f"{namespace}_{method}"

    @staticmethod
    def method_to_function_name(method: str):
        words = method.split("_")
        namespace = words[0]
        if len(words) == 2:
            method_name_split = re.split("(?<=.)(?=[A-Z])", words[1])
            method_name = "_".join([word.lower() for word in method_name_split])
        else:
            method_name = "_".join([word.lower() for word in words[1:]])
        return f"{namespace}_{method_name}"

    def eth_accounts_task(self) -> None:
        self.make_rpc_call(self.eth_accounts())

    def eth_block_number_task(self) -> None:
        self.make_rpc_call(self.eth_block_number())

    def eth_call_task(self) -> None:
        self.make_rpc_call(self.eth_call())

    def eth_chain_id_task(self) -> None:
        self.make_rpc_call(self.eth_chain_id())

    def eth_estimate_gas_task(self) -> None:
        self.make_rpc_call(self.eth_estimate_gas())

    def eth_fee_history_task(self) -> None:
        self.make_rpc_call(self.eth_fee_history())

    def eth_gas_price_task(self) -> None:
        self.make_rpc_call(self.eth_gas_price())

    def eth_get_logs_task(self) -> None:
        self.make_rpc_call(self.eth_get_logs())

    def eth_get_balance_task(self) -> None:
        self.make_rpc_call(self.eth_get_balance())

    def eth_get_block_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_by_hash())

    def eth_get_block_by_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_by_number())

    def eth_get_block_receipts_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_receipts())

    def eth_get_block_transaction_count_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_transaction_count_by_hash())

    def eth_get_block_transaction_count_by_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_transaction_count_by_number())

    def eth_get_code_task(self) -> None:
        self.make_rpc_call(self.eth_get_code())

    def eth_get_header_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_header_by_hash())

    def eth_get_header_by_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_header_by_number())

    def eth_get_transaction_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_by_hash())

    def eth_get_transaction_receipt_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_receipt())

    def eth_get_transaction_by_block_hash_and_index_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_by_block_hash_and_index())

    def eth_get_transaction_by_block_number_and_index_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_by_block_number_and_index())

    def eth_get_transaction_count_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_count())

    def eth_get_uncle_count_by_block_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_uncle_count_by_block_hash())

    def eth_get_uncle_count_by_block_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_uncle_count_by_block_number())

    def eth_max_priority_fee_per_gas_task(self) -> None:
        self.make_rpc_call(self.eth_max_priority_fee_per_gas())

    def eth_syncing_task(self) -> None:
        self.make_rpc_call(self.eth_syncing())

    @tag("debug")
    def debug_get_bad_blocks_task(self) -> None:
        self.make_rpc_call(self.debug_get_bad_blocks())

    @tag("debug")
    def debug_get_raw_block_by_number_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_block_by_number())

    @tag("debug")
    def debug_get_raw_header_by_number_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_header_by_number())

    @tag("debug")
    def debug_get_raw_receipts_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_receipts())

    @tag("debug")
    def debug_get_raw_transaction_by_hash_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_transaction_by_hash())

    @tag("debug")
    def debug_storage_range_at_task(self) -> None:
        self.make_rpc_call(self.debug_storage_range_at())

    @tag("debug")
    def debug_trace_bad_block_task(self) -> None:
        self.make_rpc_call(self.debug_trace_bad_block())

    @tag("debug")
    def debug_trace_block_task(self) -> None:
        self.make_rpc_call(self.debug_trace_block())

    @tag("debug")
    def debug_trace_block_by_hash_task(self) -> None:
        self.make_rpc_call(self.debug_trace_block_by_hash())

    @tag("debug")
    def debug_trace_block_by_number_task(self) -> None:
        self.make_rpc_call(self.debug_trace_block_by_number())

    @tag("debug")
    def debug_trace_call_task(self) -> None:
        self.make_rpc_call(self.debug_trace_call())

    @tag("debug")
    def debug_trace_transaction_task(self) -> None:
        self.make_rpc_call(self.debug_trace_transaction())

    def net_listening_task(self) -> None:
        self.make_rpc_call(self.net_listening())

    def net_peer_count_task(self) -> None:
        self.make_rpc_call(self.net_peer_count())

    def net_version_task(self) -> None:
        self.make_rpc_call(self.net_version())

    @tag("trace")
    def trace_block_task(self) -> None:
        self.make_rpc_call(self.trace_block())

    @tag("trace")
    def trace_call_task(self) -> None:
        self.make_rpc_call(self.trace_call())

    @tag("trace")
    def trace_call_many_task(self) -> None:
        self.make_rpc_call(self.trace_call_many())

    @tag("trace")
    def trace_filter_task(self) -> None:
        self.make_rpc_call(self.trace_filter())

    @tag("trace")
    def trace_replay_block_transactions_task(self) -> None:
        self.make_rpc_call(self.trace_replay_transaction())

    @tag("trace")
    def trace_replay_transaction_task(self) -> None:
        self.make_rpc_call(self.trace_replay_transaction())

    @tag("trace")
    def trace_transaction_task(self) -> None:
        self.make_rpc_call(self.trace_transaction())

    @tag("trace")
    def web3_client_version_task(self) -> None:
        self.make_rpc_call(self.web3_client_version())

    @tag("trace")
    def web3_sha3_task(self) -> None:
        self.make_rpc_call(self.web3_sha3())


class EvmUserTest(EvmUser):
    pass
