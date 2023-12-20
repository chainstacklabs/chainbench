from chainbench.test_data import EVMTestData
from chainbench.user.base import BaseBenchUser
from chainbench.util.rng import RNG, get_rng


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

    def _get_account_and_block_number_params_factory_latest(self, rng: RNG):
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
                "toBlock": hex(block_number + rng.random.randint(0, 20)),
            }
        ]

    def _eth_estimate_gas_params_factory(self, rng: RNG):
        return [
            {
                "from": self.test_data.get_random_account(rng),
                "to": self.test_data.get_random_account(rng),
            }
        ]

    @staticmethod
    def _eth_fee_history_params_factory(rng: RNG):
        return [rng.random.randint(1, 1024), "latest", [25, 75]]


class EVMMethods(EVMBenchUser):
    abstract = True

    def eth_accounts_task(self):
        self.make_call(
            method="eth_accounts",
        )

    def eth_block_number_task(self):
        self.make_call(
            method="eth_blockNumber",
        )

    def eth_chain_id_task(self):
        self.make_call(
            method="eth_chainId",
        )

    def eth_estimate_gas_task(self):
        self.make_call(
            method="eth_estimateGas",
            params=self._eth_estimate_gas_params_factory(get_rng()),
        )

    def eth_fee_history_task(self):
        self.make_call(
            method="eth_feeHistory",
            params=self._eth_fee_history_params_factory(get_rng()),
        )

    def eth_gas_price_task(self):
        self.make_call(
            method="eth_gasPrice",
        )

    def eth_get_logs_task(self):
        self.make_call(
            method="eth_getLogs",
            params=self._get_logs_params_factory(get_rng()),
        )

    def eth_get_balance_task(self):
        self.make_call(
            method="eth_getBalance",
            params=self._get_account_and_block_number_params_factory_latest(get_rng()),
        )

    def eth_get_block_by_hash_task(self):
        self.make_call(
            method="eth_getBlockByHash",
            params=self._block_by_hash_params_factory(get_rng()),
        )

    def eth_get_block_by_number_task(self):
        self.make_call(
            method="eth_getBlockByNumber",
            params=self._block_params_factory(get_rng()),
        )

    def eth_get_block_receipts_task(self):
        self.make_call(
            method="eth_getBlockReceipts",
            params=[hex(self.test_data.get_random_block_number(get_rng()))],
        )

    def eth_get_block_transaction_count_by_hash_task(self):
        self.make_call(
            method="eth_getBlockTransactionCountByHash",
            params=[self.test_data.get_random_block_hash(get_rng())],
        )

    def eth_get_block_transaction_count_by_number_task(self):
        self.make_call(
            method="eth_getBlockTransactionCountByNumber",
            params=[hex(self.test_data.get_random_block_number(get_rng()))],
        )

    def eth_get_header_by_hash_task(self):
        self.make_call(
            method="eth_getHeaderByHash",
            params=[self.test_data.get_random_block_hash(get_rng())],
        )

    def eth_get_header_by_number_task(self):
        self.make_call(
            method="eth_getHeaderByNumber",
            params=[hex(self.test_data.get_random_block_number(get_rng()))],
        )

    def eth_get_transaction_by_hash_task(self):
        self.make_call(
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(get_rng()),
        )

    def eth_get_transaction_receipt_task(self):
        self.make_call(
            method="eth_getTransactionReceipt",
            params=self._transaction_by_hash_params_factory(get_rng()),
        )

    def eth_get_transaction_by_block_hash_and_index_task(self):
        self.make_call(
            method="eth_getTransactionByBlockHashAndIndex",
            params=[
                self.test_data.get_random_block_hash(get_rng()),
                hex(get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_by_block_number_and_index_task(self):
        self.make_call(
            method="eth_getTransactionByBlockNumberAndIndex",
            params=[
                hex(self.test_data.get_random_block_number(get_rng())),
                hex(get_rng().random.randint(0, 20)),
            ],
        )

    def eth_get_transaction_count_task(self):
        self.make_call(
            method="eth_getTransactionCount",
            params=self._get_account_and_block_number_params_factory_latest(get_rng()),
        )

    def eth_get_uncle_count_by_block_hash_task(self):
        self.make_call(
            method="eth_getUncleCountByBlockHash",
            params=[self.test_data.get_random_block_hash(get_rng())],
        )

    def eth_get_uncle_count_by_block_number_task(self):
        self.make_call(
            method="eth_getUncleCountByBlockNumber",
            params=[hex(self.test_data.get_random_block_number(get_rng()))],
        )

    def eth_max_priority_fee_per_gas_task(self):
        self.make_call(
            method="eth_maxPriorityFeePerGas",
        )

    def eth_syncing_task(self):
        self.make_call(
            method="eth_syncing",
        )

    def debug_trace_block_by_hash_task(self):
        self.make_call(
            method="debug_traceBlockByHash",
            params=self._trace_block_by_hash_params_factory(get_rng()),
        )

    def debug_trace_block_by_number_task(self):
        self.make_call(
            method="debug_traceBlockByNumber",
            params=self._trace_block_by_number_params_factory(get_rng()),
        )

    def debug_trace_call_task(self):
        self.make_call(
            method="debug_traceCall",
            params=self._trace_call_params_factory(get_rng()),
        )

    def debug_trace_transaction_task(self):
        self.make_call(
            method="debug_traceTransaction",
            params=self._trace_transaction_params_factory(get_rng()),
        )

    def net_listening_task(self):
        self.make_call(
            method="net_listening",
        )

    def net_peer_count_task(self):
        self.make_call(
            method="net_peerCount",
        )

    def net_version_task(self):
        self.make_call(
            method="net_version",
        )

    def trace_block_task(self):
        self.make_call(
            method="trace_block",
            params=self._block_params_factory(get_rng()),
        )

    def trace_replay_block_transactions_task(self):
        self.make_call(
            method="trace_replayBlockTransactions",
            params=self._trace_replay_block_transaction_params_factory(get_rng()),
        )

    def trace_replay_transaction_task(self):
        self.make_call(
            method="trace_replayTransaction",
            params=self._trace_replay_transaction_params_factory(get_rng()),
        )

    def web3_client_version_task(self):
        self.make_call(
            method="web3_clientVersion",
        )

    def web3_sha3_task(self):
        self.make_call(
            method="web3_sha3",
            params=[self.test_data.get_random_tx_hash(get_rng())],
        )
