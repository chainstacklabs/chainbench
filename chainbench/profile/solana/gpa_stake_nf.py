from typing import Optional

from locust import task, constant_pacing
from random import Random

from chainbench.user.jsonrpc import RpcCall
from chainbench.user.protocol.solana import SolanaUser


class SolProgram:
    def __init__(self, address: str, name: Optional[str] = None, filter_bytes: Optional[list[str]] = None, offset: Optional[int] = None):
        self._name = name
        self.address = address
        self.filter_bytes = filter_bytes
        self.offset = offset
        self.rand = Random(0)

    def get_random_commitment(self):
        return self.rand.choice(["processed", "confirmed", "finalized"])

    def get_random_filter(self):
        return self.rand.choice(self.filter_bytes)

    @property
    def name(self):
        return self.address[:5] if self._name is None else self._name

    def get_rpc_call(self):
        filters = [
            {
                "memcmp": {
                    "bytes": self.get_random_filter(),
                    "offset": self.offset,
                    "encoding": "base64",
                }
            }
        ] if self.filter_bytes is not None and self.offset is not None else None
        config: dict = {
                    "encoding": "base64",
                    # "commitment": self.get_random_commitment(),
                    "commitment": "finalized", # hardcoded to finalized for now...
                    "dataSlice": {
                        "offset": 0,
                        "length": 16
                    }
                }
        if filters is not None:
            config["filters"] = filters
        return RpcCall(
            method="getProgramAccounts",
            params=[
                self.address,
                config,
            ],
        )


stake_program = SolProgram(
    address="Stake11111111111111111111111111111111111111",
    name="stake",
)

hyperlane_program = SolProgram(
    address="E588QtVUvresuXq2KoNEwAmoifCzYGpRBdHByN9KQMbi",
    name="hyperlane",
)

derp_program = SolProgram(
    address="DERP2sf1Nak1R7s5HVgQD9WcQM1X9CKh5Ru5PNafAsPg",
    name="derp",
)

jupiter_program = SolProgram(
    address="PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu",
    name="jupiter",
)

whirlpools_program = SolProgram(
    address="whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    name="whirlpools",
)

meteora_dlmm_program = SolProgram(
    address="LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
    name="meteora_dlmm",
)

byreal_program = SolProgram(
    address="REALQqNEomY6cQGZJUGwywTBD2UmDT32rZcNnfxQ5N2",
    name="byreal",
)

meteora_pools_program = SolProgram(
    address="Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
    name="meteora_pools",
)

raydium_program = SolProgram(
    address="CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",
    name="raydium",
)

pancakeswap_program = SolProgram(
    address="HpNfyc2Saw7RKkQd8nEL4khUcuPhQ7WwY1B2qjx8jxFq",
    name="pancakeswap",
)

ore_program = SolProgram(
    address="oreV2ZymfyeXgNgBdqMkumTqqAprVqgBWQfoYkrtKWQ",
    name="ore",
)

class SolanaGPAUser(SolanaUser):
    abstract = True
    def call_gpa(self, program: SolProgram):
        self.make_rpc_call(
            program.get_rpc_call(),
            name="getProgramAccounts" + program.name.capitalize(),
        )


class GPAStake(SolanaGPAUser):
    wait_time = constant_pacing(1)
    @task
    def get_program_accounts_stake_task(self) -> None:
        self.call_gpa(stake_program)
#
# class GPAHyper(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_hyperlane_task(self) -> None:
#         self.call_gpa(hyperlane_program)
#
# class GPADerp(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_derp_task(self) -> None:
#         self.call_gpa(derp_program)
#
# class GPAJupiter(SolanaGPAUser):
#     weight = 0
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_jupiter_task(self) -> None:
#         self.call_gpa(jupiter_program)
#
# class GPAWhirl(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_whirlpools_task(self) -> None:
#         self.call_gpa(whirlpools_program)
#
# class GPAMetDLMM(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_meteora_dlmm_task(self) -> None:
#         self.call_gpa(meteora_dlmm_program)
#
# class GPAByreal(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_byreal_task(self) -> None:
#         self.call_gpa(byreal_program)
#
# class GPAMetPools(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_meteora_pools_task(self) -> None:
#         self.call_gpa(meteora_pools_program)
#
# # class GPARaydium(SolanaGPAUser):
# #     weight = 1
#
#     # @task
#     # def get_program_accounts_raydium_task(self) -> None:
#     #     self.call_gpa(raydium_program)
#
# class GPAPancake(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_pancakeswap_task(self) -> None:
#         self.call_gpa(pancakeswap_program)
#
# class GPAOre(SolanaGPAUser):
#     weight = 10
#     wait_time = constant_pacing(1)
#
#     @task
#     def get_program_accounts_ore_task(self) -> None:
#         self.call_gpa(ore_program)
