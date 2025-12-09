from typing import Optional

from locust import task
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
    filter_bytes=["KlEIdCea2Sk=", "1gRdtuwdnY8=", "EDxxgSjTMKE=", "5tH6d9cuU1I=", "8PZxLJhlpGY=", "MZsSLiiDWbQ=", "vV/xHxU3/UQ="],
    offset=12
)

hyperlane_program = SolProgram(
    address="E588QtVUvresuXq2KoNEwAmoifCzYGpRBdHByN9KQMbi",
    name="hyperlane",
    filter_bytes=["SGouAADURn4RAAAAAN9b5Q==", "SAXQAwD4X4ATAAAAAEur6g==", "RCYVAgAAAAAAqcz6g47Dpw==", "SNA3BACwBuUTAAAAANllrA==", "SBBXAgBVQLISAAAAAA7Suw=="],
    offset=8
)

derp_program = SolProgram(
    address="DERP2sf1Nak1R7s5HVgQD9WcQM1X9CKh5Ru5PNafAsPg",
    name="derp",
    filter_bytes=["AH17119gpMI=", "mi+XRgiAzuc=", "YZydvcJJCA8=", ],
    offset=0
)

jupiter_program = SolProgram(
    address="PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu",
    name="jupiter",
    filter_bytes=["nBgxGb+hnXE=", "JvRlEb/wcjw=", "hNpHpIy1d2A=", "LKDGGmzRPdw=", "tAKIBM2ctxk=", "0E8ZDGwQ9Bs="],
    offset=8
)

whirlpools_program = SolProgram(
    address="whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    name="whirlpools",
    filter_bytes=["AGABAAAAAAA=", "AAAAAKdSbY0=", "AIgGAAAAAAA=", "oDUAAAAAAAA=", "AMACAAAAAAA=", "ybQ8WL8BjqQ="],
    offset=8
)

meteora_dlmm_program = SolProgram(
    address="LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
    name="meteora_dlmm",
    filter_bytes=["9P////////8=", "CwAAAAAAAAA=", "crGmppy8dsU=", "FQAAAAAAAAA=", "tFlOyyi2l30=", "5P////////8="],
    offset=8
)

byreal_program = SolProgram(
    address="REALQqNEomY6cQGZJUGwywTBD2UmDT32rZcNnfxQ5N2",
    name="byreal",
    filter_bytes=["/gQu8broD5g=", "/p/l1dc7Yh4=", "/wQu8broD5g=", "/y8FhezHWec=", "/em4Nj2MfbY=", "acEauExBB/o="],
    offset=8
)

meteora_pools_program = SolProgram(
    address="Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
    name="meteora_pools",
)

raydium_program = SolProgram(
    address="CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",
    name="raydium",
    filter_bytes=["izFdJVLyvnc=", "Xaxx7B6DSEA=", "+2fqeyM2Fgg=", "/nTnAJwTH4U=", "/TmA0EzfeJI=", "/h8sSv5cosk="],
    offset=0
)

pancakeswap_program = SolProgram(
    address="HpNfyc2Saw7RKkQd8nEL4khUcuPhQ7WwY1B2qjx8jxFq",
    name="pancakeswap",
    filter_bytes=["/g8v5TUg7Y4=", "/7a/3HmNTEA=", "/TKV+aeUlGk=", "/7a/3HmNTEA=", "/xfBfJmKcQg=", "/zKV+aeUlGk="],
    offset=0
)

ore_program = SolProgram(
    address="oreV2ZymfyeXgNgBdqMkumTqqAprVqgBWQfoYkrtKWQ",
    name="ore",
    filter_bytes=["CG+Rg7YASun0nieD5b7psw==", "GfIZMI88YqHyH2NFakVsmQ==", "9G5FkSGQRbb343CTJLC1wA==", "KnUYQIOAS2D3W2DjjmZkNw==", "inwdx9HkQG+MvZtoEPpDHw=="],
    offset=8
)


class GetProgramAccounts(SolanaUser):
    def call_gpa(self, program: SolProgram):
        self.make_rpc_call(
            program.get_rpc_call(),
            name="getProgramAccounts" + program.name.capitalize(),
        )

    @task(58)
    def get_program_accounts_stake_task(self) -> None:
        self.call_gpa(stake_program)

    @task(55)
    def get_program_accounts_hyperlane_task(self) -> None:
        self.call_gpa(hyperlane_program)

    @task(13)
    def get_program_accounts_derp_task(self) -> None:
        self.call_gpa(derp_program)

    @task(4)
    def get_program_accounts_jupiter_task(self) -> None:
        self.call_gpa(jupiter_program)

    @task(2)
    def get_program_accounts_whirlpools_task(self) -> None:
        self.call_gpa(whirlpools_program)

    @task(2)
    def get_program_accounts_meteora_dlmm_task(self) -> None:
        self.call_gpa(meteora_dlmm_program)

    @task(1)
    def get_program_accounts_byreal_task(self) -> None:
        self.call_gpa(byreal_program)

    @task(1)
    def get_program_accounts_meteora_pools_task(self) -> None:
        self.call_gpa(meteora_pools_program)

    # @task(1)
    # def get_program_accounts_raydium_task(self) -> None:
    #     self.call_gpa(raydium_program)

    @task(1)
    def get_program_accounts_pancakeswap_task(self) -> None:
        self.call_gpa(pancakeswap_program)

    @task(1)
    def get_program_accounts_ore_task(self) -> None:
        self.call_gpa(ore_program)
