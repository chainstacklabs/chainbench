from locust import task

from chainbench.user.protocol.solana import SolanaUser
from chainbench.util.jsonrpc import RpcCall


class SolanaGetBlock(SolanaUser):
    @task
    def get_block_task(self):
        self.make_rpc_call(
            RpcCall(
                method="getBlock",
                params=[
                    self.test_data.get_random_block_number(self.rng.get_rng()),
                    {
                        "encoding": "jsonParsed",
                        "transactionDetails": "full",
                        "maxSupportedTransactionVersion": 0,
                    },
                ]
            )
        )
