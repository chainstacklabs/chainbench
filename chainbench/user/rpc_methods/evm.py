from chainbench.user.evm import EvmUser
from chainbench.user.http import RpcCall


class EvmRpcMethods(EvmUser):
    abstract = True

    @staticmethod
    def eth_accounts_rpc() -> RpcCall:
        return RpcCall(method="eth_accounts")

    @staticmethod
    def eth_block_number_rpc() -> RpcCall:
        return RpcCall(method="eth_blockNumber")

    def eth_call_rpc(self) -> RpcCall:
        return RpcCall(method="eth_call", params=self._erc20_eth_call_params_factory(self.rng.get_rng()))

    @staticmethod
    def eth_chain_id_rpc() -> RpcCall:
        return RpcCall(method="eth_chainId")

    def eth_estimate_gas_rpc(self) -> RpcCall:
        return RpcCall(method="eth_estimateGas", params=self._erc20_eth_call_params_factory(self.rng.get_rng()))

    def eth_fee_history_rpc(self) -> RpcCall:
        return RpcCall(method="eth_feeHistory", params=self._eth_fee_history_params_factory(self.rng.get_rng()))

    @staticmethod
    def eth_gas_price_rpc() -> RpcCall:
        return RpcCall(method="eth_gasPrice")

    def eth_get_logs_rpc(self) -> RpcCall:
        return RpcCall(method="eth_getLogs", params=self._get_logs_params_factory(self.rng.get_rng()))

    def eth_get_balance_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getBalance", params=self._get_account_and_block_number_params_factory_latest(self.rng.get_rng())
        )

    def eth_get_block_by_hash_rpc(self) -> RpcCall:
        return RpcCall(method="eth_getBlockByHash", params=self._block_by_hash_params_factory(self.rng.get_rng()))

    def eth_get_block_by_number_rpc(self) -> RpcCall:
        return RpcCall(method="eth_getBlockByNumber", params=self._block_params_factory())

    def eth_get_block_receipts_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getBlockReceipts", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def eth_get_block_transaction_count_by_hash_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getBlockTransactionCountByHash",
            params=[self.test_data.get_random_block_hash(self.rng.get_rng())],
        )

    def eth_get_block_transaction_count_by_number_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getBlockTransactionCountByNumber",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    def eth_get_code_rpc(self) -> RpcCall:
        return RpcCall(method="eth_getCode", params=self._erc20_eth_get_code_params_factory(self.rng.get_rng()))

    def eth_get_header_by_hash_rpc(self) -> RpcCall:
        return RpcCall(method="eth_getHeaderByHash", params=[self.test_data.get_random_block_hash(self.rng.get_rng())])

    def eth_get_header_by_number_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getHeaderByNumber", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def eth_get_transaction_by_hash_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionByHash", params=self._transaction_by_hash_params_factory(self.rng.get_rng())
        )

    def eth_get_transaction_receipt_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionReceipt", params=self._transaction_by_hash_params_factory(self.rng.get_rng())
        )

    def eth_get_transaction_by_block_hash_and_index_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionByBlockHashAndIndex",
            params=[
                self.test_data.get_random_block_hash(self.rng.get_rng()),
                hex(self.rng.get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_by_block_number_and_index_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionByBlockNumberAndIndex",
            params=[
                hex(self.test_data.get_random_block_number(self.rng.get_rng())),
                hex(self.rng.get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_count_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getTransactionCount",
            params=self._get_account_and_block_number_params_factory_latest(self.rng.get_rng()),
        )

    def eth_get_uncle_count_by_block_hash_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getUncleCountByBlockHash", params=[self.test_data.get_random_block_hash(self.rng.get_rng())]
        )

    def eth_get_uncle_count_by_block_number_rpc(self) -> RpcCall:
        return RpcCall(
            method="eth_getUncleCountByBlockNumber",
            params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))],
        )

    @staticmethod
    def eth_max_priority_fee_per_gas_rpc() -> RpcCall:
        return RpcCall(method="eth_maxPriorityFeePerGas")

    @staticmethod
    def eth_syncing_rpc() -> RpcCall:
        return RpcCall(method="eth_syncing")

    # TODO: Implement tags for rpc methods as well to enable filtering for batch requests

    @staticmethod
    def debug_get_bad_blocks_rpc() -> RpcCall:
        return RpcCall(method="debug_getBadBlocks")

    def debug_get_raw_block_by_number_rpc(self) -> RpcCall:
        return RpcCall(
            method="debug_getRawBlock", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def debug_get_raw_header_by_number_rpc(self) -> RpcCall:
        return RpcCall(
            method="debug_getRawHeader", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def debug_get_raw_receipts_by_number_rpc(self) -> RpcCall:
        return RpcCall(
            method="debug_getRawReceipts", params=[hex(self.test_data.get_random_block_number(self.rng.get_rng()))]
        )

    def debug_get_raw_transaction_by_hash_rpc(self) -> RpcCall:
        return RpcCall(method="debug_getRawTransaction", params=[self.test_data.get_random_tx_hash(self.rng.get_rng())])

    def debug_trace_bad_block_rpc(self) -> RpcCall:
        return RpcCall(method="debug_traceBadBlock", params=[self.test_data.get_random_block_hash(self.rng.get_rng())])

    def debug_trace_block_rpc(self) -> RpcCall:
        return RpcCall(method="debug_traceBlock", params=self._block_params_factory())

    def debug_trace_block_by_hash_rpc(self) -> RpcCall:
        return RpcCall(
            method="debug_traceBlockByHash", params=self._debug_trace_block_by_hash_params_factory(self.rng.get_rng())
        )

    def debug_trace_block_by_number_rpc(self) -> RpcCall:
        return RpcCall(method="debug_traceBlockByNumber", params=self._debug_trace_block_by_number_params_factory())

    def debug_trace_call_rpc(self) -> RpcCall:
        return RpcCall(method="debug_traceCall", params=self._debug_trace_call_params_factory(self.rng.get_rng()))

    def debug_trace_transaction_rpc(self) -> RpcCall:
        return RpcCall(
            method="debug_traceTransaction", params=self._debug_trace_transaction_params_factory(self.rng.get_rng())
        )

    @staticmethod
    def net_listening_rpc() -> RpcCall:
        return RpcCall(method="net_listening")

    @staticmethod
    def net_peer_count_rpc() -> RpcCall:
        return RpcCall(method="net_peerCount")

    @staticmethod
    def net_version_rpc() -> RpcCall:
        return RpcCall(method="net_version")

    def trace_block_rpc(self) -> RpcCall:
        return RpcCall(method="trace_block", params=self._block_params_factory())

    def trace_replay_block_transactions_rpc(self) -> RpcCall:
        return RpcCall(
            method="trace_replayBlockTransactions", params=self._trace_replay_block_transaction_params_factory()
        )

    def trace_replay_transaction_rpc(self) -> RpcCall:
        return RpcCall(
            method="trace_replayTransaction", params=self._trace_replay_transaction_params_factory(self.rng.get_rng())
        )

    def trace_transaction_rpc(self) -> RpcCall:
        return RpcCall(method="trace_transaction", params=[self.test_data.get_random_tx_hash(self.rng.get_rng())])

    @staticmethod
    def web3_client_version_rpc() -> RpcCall:
        return RpcCall(method="web3_clientVersion")

    def web3_sha3_rpc(self) -> RpcCall:
        return RpcCall(method="web3_sha3", params=[self.test_data.get_random_tx_hash(self.rng.get_rng())])
