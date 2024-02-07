import re
import typing as t

from locust import task

from chainbench.user.evm import EvmUser


class EvmMethods(EvmUser):
    abstract = True

    @staticmethod
    def task_to_method(task_name: str) -> str:
        task_name_stripped = task_name.replace("_task", "")
        words = task_name_stripped.split("_")
        namespace = words[0]
        method = "".join([words[1]] + [word.capitalize() for word in words[2:]])
        return f"{namespace}_{method}"

    def method_to_task_function(self, method: str) -> t.Callable:
        words = method.split("_")
        namespace = words[0]
        method_name_split = re.split("(?<=.)(?=[A-Z])", words[1])
        method_name = "_".join([word.lower() for word in method_name_split])
        return getattr(self, f"{namespace}_{method_name}_task")

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


class TestEvmMethod(EvmMethods):
    @task
    def run_task(self) -> None:
        self.method_to_task_function(self.environment.parsed_options.method)()
