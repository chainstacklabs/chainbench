from locust import task

from chainbench.user.jsonrpc import RpcCall
from chainbench.user.protocol.solana import SolanaUser


class GetProgramAccounts(SolanaUser):
    @task
    def get_program_accounts_stake_task(self) -> None:
        self.make_rpc_call(
            RpcCall(
                method="getProgramAccounts",
                params=[
                    "Stake11111111111111111111111111111111111111",
                    {
                        "encoding": "jsonParsed",
                        "commitment": "finalized",
                        "filters": [
                            {"memcmp": {"bytes": "2K9XJAj3VtojUhyKdXVfGnueSvnyFNfSACkn1CwgBees", "offset": 12}}
                        ],
                    },
                ],
            ),
            name="getProgramAccounts_stake",
        )
