from locust import task

from chainbench.user.jsonrpc import RpcCall
from chainbench.user.protocol.solana import SolanaUser


class GetProgramAccounts(SolanaUser):
    @task
    def get_program_accounts_shark_task(self) -> None:
        self.make_rpc_call(
            RpcCall(
                method="getProgramAccounts",
                params=[
                    "SharkXwkS3h24fJ2LZvgG5tPbsH3BKQYuAtKdqskf1f",
                    {"encoding": "base64", "commitment": "confirmed"},
                ],
            ),
            name="getProgramAccounts_shark",
        )
