import re
import typing as t

from locust import tag, task

from chainbench.user.rpc_methods.evm import EvmRpcMethods


class EvmTasks(EvmRpcMethods):
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
        self.make_rpc_call(self.eth_accounts_rpc())

    def eth_block_number_task(self) -> None:
        self.make_rpc_call(self.eth_block_number_rpc())

    def eth_call_task(self) -> None:
        self.make_rpc_call(self.eth_call_rpc())

    def eth_chain_id_task(self) -> None:
        self.make_rpc_call(self.eth_chain_id_rpc())

    def eth_estimate_gas_task(self) -> None:
        self.make_rpc_call(self.eth_estimate_gas_rpc())

    def eth_fee_history_task(self) -> None:
        self.make_rpc_call(self.eth_fee_history_rpc())

    def eth_gas_price_task(self) -> None:
        self.make_rpc_call(self.eth_gas_price_rpc())

    def eth_get_logs_task(self) -> None:
        self.make_rpc_call(self.eth_get_logs_rpc())

    def eth_get_balance_task(self) -> None:
        self.make_rpc_call(self.eth_get_balance_rpc())

    def eth_get_block_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_by_hash_rpc())

    def eth_get_block_by_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_by_number_rpc())

    def eth_get_block_receipts_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_receipts_rpc())

    def eth_get_block_transaction_count_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_transaction_count_by_hash_rpc())

    def eth_get_block_transaction_count_by_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_block_transaction_count_by_number_rpc())

    def eth_get_code_task(self) -> None:
        self.make_rpc_call(self.eth_get_code_rpc())

    def eth_get_header_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_header_by_hash_rpc())

    def eth_get_header_by_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_header_by_number_rpc())

    def eth_get_transaction_by_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_by_hash_rpc())

    def eth_get_transaction_receipt_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_receipt_rpc())

    def eth_get_transaction_by_block_hash_and_index_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_by_block_hash_and_index_rpc())

    def eth_get_transaction_by_block_number_and_index_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_by_block_number_and_index_rpc())

    def eth_get_transaction_count_task(self) -> None:
        self.make_rpc_call(self.eth_get_transaction_count_rpc())

    def eth_get_uncle_count_by_block_hash_task(self) -> None:
        self.make_rpc_call(self.eth_get_uncle_count_by_block_hash_rpc())

    def eth_get_uncle_count_by_block_number_task(self) -> None:
        self.make_rpc_call(self.eth_get_uncle_count_by_block_number_rpc())

    def eth_max_priority_fee_per_gas_task(self) -> None:
        self.make_rpc_call(self.eth_max_priority_fee_per_gas_rpc())

    def eth_syncing_task(self) -> None:
        self.make_rpc_call(self.eth_syncing_rpc())

    @tag("debug")
    def debug_get_bad_blocks_task(self) -> None:
        self.make_rpc_call(self.debug_get_bad_blocks_rpc())

    @tag("debug")
    def debug_get_raw_block_by_number_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_block_by_number_rpc())

    @tag("debug")
    def debug_get_raw_header_by_number_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_header_by_number_rpc())

    @tag("debug")
    def debug_get_raw_receipts_by_number_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_receipts_by_number_rpc())

    @tag("debug")
    def debug_get_raw_transaction_by_hash_task(self) -> None:
        self.make_rpc_call(self.debug_get_raw_transaction_by_hash_rpc())

    @tag("debug")
    def debug_trace_bad_block_task(self) -> None:
        self.make_rpc_call(self.debug_trace_bad_block_rpc())

    @tag("debug")
    def debug_trace_block_task(self) -> None:
        self.make_rpc_call(self.debug_trace_block_rpc())

    @tag("debug")
    def debug_trace_block_by_hash_task(self) -> None:
        self.make_rpc_call(self.debug_trace_block_by_hash_rpc())

    @tag("debug")
    def debug_trace_block_by_number_task(self) -> None:
        self.make_rpc_call(self.debug_trace_block_by_number_rpc())

    @tag("debug")
    def debug_trace_call_task(self) -> None:
        self.make_rpc_call(self.debug_trace_call_rpc())

    @tag("debug")
    def debug_trace_transaction_task(self) -> None:
        self.make_rpc_call(self.debug_trace_transaction_rpc())

    def net_listening_task(self) -> None:
        self.make_rpc_call(self.net_listening_rpc())

    def net_peer_count_task(self) -> None:
        self.make_rpc_call(self.net_peer_count_rpc())

    def net_version_task(self) -> None:
        self.make_rpc_call(self.net_version_rpc())

    @tag("trace")
    def trace_block_task(self) -> None:
        self.make_rpc_call(self.trace_block_rpc())

    @tag("trace")
    def trace_replay_block_transactions_task(self) -> None:
        self.make_rpc_call(self.trace_replay_transaction_rpc())

    @tag("trace")
    def trace_replay_transaction_task(self) -> None:
        self.make_rpc_call(self.trace_replay_transaction_rpc())

    @tag("trace")
    def trace_transaction_task(self) -> None:
        self.make_rpc_call(self.trace_transaction_rpc())

    @tag("trace")
    def web3_client_version_task(self) -> None:
        self.make_rpc_call(self.web3_client_version_rpc())

    @tag("trace")
    def web3_sha3_task(self) -> None:
        self.make_rpc_call(self.web3_sha3_rpc())


class TestEvmMethod(EvmTasks):
    @task
    def run_task(self) -> None:
        self.method_to_task_function(self.environment.parsed_options.method)()
