# """
# Ethereum General profile (batch).
# """
import random

from locust import constant_pacing, task

from chainbench.user.http import RpcCall
from chainbench.user.rpc_methods.evm import EvmRpcMethods
from chainbench.user.tasks.common import expand_batch_rpc


class EthereumBatchProfile(EvmRpcMethods):
    wait_time = constant_pacing(1)

    @task
    def batch_rpc_call_task(self):
        calls_per_batch = 50
        rpc_calls: list[RpcCall] = expand_batch_rpc(
            {
                self.eth_call_rpc(): 259,
                self.eth_get_transaction_receipt_rpc(): 62,
                self.eth_block_number_rpc(): 49,
                self.eth_get_balance_rpc(): 31,
                self.eth_chain_id_rpc(): 28,
                self.eth_get_block_by_number_rpc(): 23,
                self.eth_get_transaction_by_hash_rpc(): 21,
                self.eth_get_logs_rpc(): 13,
                self.trace_transaction_rpc(): 8,
                self.web3_client_version_rpc(): 5,
            }
        )
        random_rpc_calls = random.choices(rpc_calls, k=calls_per_batch)
        self.make_batch_rpc_call(random_rpc_calls)
