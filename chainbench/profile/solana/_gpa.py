"""Shared program definitions and user-class factories for the Solana
getProgramAccounts (GPA) profiles.

The leading underscore keeps this module out of locust's profile discovery
(see `get_abspaths_in` in locust.argument_parser), so it is not runnable
as a profile itself.
"""
from random import Random

from chainbench.user.jsonrpc import RpcCall
from chainbench.user.protocol.solana import SolanaUser


class SolProgram:
    def __init__(
        self,
        address: str,
        name: str | None = None,
        filter_bytes: list[str] | None = None,
        offset: int | None = None,
    ):
        self._name = name
        self.address = address
        self.filter_bytes = filter_bytes
        self.offset = offset
        # Fixed seed so filter selection is reproducible across runs
        self.rand = Random(0)

    @property
    def name(self) -> str:
        return self.address[:5] if self._name is None else self._name

    def get_rpc_call(self, use_filters: bool = True, data_slice: bool = True) -> RpcCall:
        config: dict = {
            "encoding": "base64",
            "commitment": "finalized",  # hardcoded to finalized for now...
        }
        if data_slice:
            config["dataSlice"] = {"offset": 0, "length": 16}
        if use_filters and self.filter_bytes is not None and self.offset is not None:
            config["filters"] = [
                {
                    "memcmp": {
                        "bytes": self.rand.choice(self.filter_bytes),
                        "offset": self.offset,
                        "encoding": "base64",
                    }
                }
            ]
        return RpcCall(
            method="getProgramAccounts",
            params=[
                self.address,
                config,
            ],
        )


PROGRAMS: dict[str, SolProgram] = {
    program.name: program
    for program in [
        SolProgram(
            address="Stake11111111111111111111111111111111111111",
            name="stake",
            filter_bytes=[
                "KlEIdCea2Sk=",
                "1gRdtuwdnY8=",
                "EDxxgSjTMKE=",
                "5tH6d9cuU1I=",
                "8PZxLJhlpGY=",
                "MZsSLiiDWbQ=",
                "vV/xHxU3/UQ=",
            ],
            offset=12,
        ),
        SolProgram(
            address="E588QtVUvresuXq2KoNEwAmoifCzYGpRBdHByN9KQMbi",
            name="hyperlane",
            filter_bytes=[
                "SGouAADURn4RAAAAAN9b5Q==",
                "SAXQAwD4X4ATAAAAAEur6g==",
                "RCYVAgAAAAAAqcz6g47Dpw==",
                "SNA3BACwBuUTAAAAANllrA==",
                "SBBXAgBVQLISAAAAAA7Suw==",
            ],
            offset=8,
        ),
        SolProgram(
            address="DERP2sf1Nak1R7s5HVgQD9WcQM1X9CKh5Ru5PNafAsPg",
            name="derp",
            filter_bytes=["AH17119gpMI=", "mi+XRgiAzuc=", "YZydvcJJCA8="],
            offset=0,
        ),
        SolProgram(
            address="PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu",
            name="jupiter",
            filter_bytes=[
                "nBgxGb+hnXE=",
                "JvRlEb/wcjw=",
                "hNpHpIy1d2A=",
                "LKDGGmzRPdw=",
                "tAKIBM2ctxk=",
                "0E8ZDGwQ9Bs=",
            ],
            offset=8,
        ),
        SolProgram(
            address="whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
            name="whirlpools",
            filter_bytes=[
                "AGABAAAAAAA=",
                "AAAAAKdSbY0=",
                "AIgGAAAAAAA=",
                "oDUAAAAAAAA=",
                "AMACAAAAAAA=",
                "ybQ8WL8BjqQ=",
            ],
            offset=8,
        ),
        SolProgram(
            address="LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
            name="meteora_dlmm",
            filter_bytes=[
                "9P////////8=",
                "CwAAAAAAAAA=",
                "crGmppy8dsU=",
                "FQAAAAAAAAA=",
                "tFlOyyi2l30=",
                "5P////////8=",
            ],
            offset=8,
        ),
        SolProgram(
            address="REALQqNEomY6cQGZJUGwywTBD2UmDT32rZcNnfxQ5N2",
            name="byreal",
            filter_bytes=[
                "/gQu8broD5g=",
                "/p/l1dc7Yh4=",
                "/wQu8broD5g=",
                "/y8FhezHWec=",
                "/em4Nj2MfbY=",
                "acEauExBB/o=",
            ],
            offset=8,
        ),
        SolProgram(
            address="Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
            name="meteora_pools",
        ),
        SolProgram(
            address="CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",
            name="raydium",
            filter_bytes=[
                "izFdJVLyvnc=",
                "Xaxx7B6DSEA=",
                "+2fqeyM2Fgg=",
                "/nTnAJwTH4U=",
                "/TmA0EzfeJI=",
                "/h8sSv5cosk=",
            ],
            offset=0,
        ),
        SolProgram(
            address="HpNfyc2Saw7RKkQd8nEL4khUcuPhQ7WwY1B2qjx8jxFq",
            name="pancakeswap",
            filter_bytes=[
                "/g8v5TUg7Y4=",
                "/7a/3HmNTEA=",
                "/TKV+aeUlGk=",
                "/7a/3HmNTEA=",
                "/xfBfJmKcQg=",
                "/zKV+aeUlGk=",
            ],
            offset=0,
        ),
        SolProgram(
            address="oreV2ZymfyeXgNgBdqMkumTqqAprVqgBWQfoYkrtKWQ",
            name="ore",
            filter_bytes=[
                "CG+Rg7YASun0nieD5b7psw==",
                "GfIZMI88YqHyH2NFakVsmQ==",
                "9G5FkSGQRbb343CTJLC1wA==",
                "KnUYQIOAS2D3W2DjjmZkNw==",
                "inwdx9HkQG+MvZtoEPpDHw==",
            ],
            offset=8,
        ),
    ]
}

# Synthetic per-program request-rate weights approximating a heavy-tailed
# real-world traffic mix (raydium excluded). Illustrative, not measured.
TRAFFIC_WEIGHTS: dict[str, int] = {
    "stake": 60,
    "hyperlane": 50,
    "derp": 15,
    "jupiter": 5,
    "whirlpools": 2,
    "meteora_dlmm": 2,
    "byreal": 1,
    "meteora_pools": 1,
    "pancakeswap": 1,
    "ore": 1,
}

EQUAL_WEIGHTS: dict[str, int] = {name: 1 for name in TRAFFIC_WEIGHTS}


def _gpa_task(program: SolProgram, use_filters: bool, data_slice: bool):
    def gpa_task(user: SolanaUser) -> None:
        user.make_rpc_call(
            program.get_rpc_call(use_filters=use_filters, data_slice=data_slice),
            name="getProgramAccounts" + program.name.capitalize(),
        )

    gpa_task.__name__ = f"get_program_accounts_{program.name}_task"
    return gpa_task


def create_gpa_users(
    weights: dict[str, int],
    wait_time=None,
    use_filters: bool = True,
    data_slice: bool = True,
) -> dict[str, type[SolanaUser]]:
    """Create one locust user class per program.

    Register the classes in a profile with ``globals().update(create_gpa_users(...))``.
    """
    users: dict[str, type[SolanaUser]] = {}
    for program_name, weight in weights.items():
        program = PROGRAMS[program_name]
        attrs: dict = {
            "weight": weight,
            "tasks": [_gpa_task(program, use_filters, data_slice)],
        }
        if wait_time is not None:
            attrs["wait_time"] = wait_time
        class_name = "GPA" + program.name.title().replace("_", "")
        users[class_name] = type(class_name, (SolanaUser,), attrs)
    return users


def create_gpa_taskset_user(
    weights: dict[str, int],
    wait_time=None,
    use_filters: bool = True,
    data_slice: bool = True,
    class_name: str = "GetProgramAccounts",
) -> type[SolanaUser]:
    """Create a single user class running all programs as weighted tasks."""
    tasks = {
        _gpa_task(PROGRAMS[program_name], use_filters, data_slice): weight
        for program_name, weight in weights.items()
    }
    attrs: dict = {"tasks": tasks}
    if wait_time is not None:
        attrs["wait_time"] = wait_time
    return type(class_name, (SolanaUser,), attrs)
