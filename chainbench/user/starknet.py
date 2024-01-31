import typing as t

from chainbench.test_data import StarkNetTestData
from chainbench.test_data.blockchain import Account, TxHash
from chainbench.util.rng import RNG

from .http import JsonRpcUser


class StarkNetUser(JsonRpcUser):
    abstract = True
    test_data = StarkNetTestData()

    @staticmethod
    def _call_params_factory(rng: RNG) -> dict[str, t.Any]:
        return {
            "request": {
                "contract_address": "0x10884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28",
                "entry_point_selector": "0x279193ae67f7ef3a6be330f5bd004266a0ec3fd5a6f7d2fe71a2096b3101578",
                "calldata": [hex(rng.random.randint(1, 8))],
            },
            "block_id": "latest",
        }

    @staticmethod
    def _simulate_transaction_params_factory(rng: RNG) -> list[dict | list[dict] | list[str]]:
        return [
            {"block_number": rng.random.randint(124000, 124400)},
            [
                {
                    "type": "INVOKE",
                    "max_fee": "0x0",
                    "version": "0x100000000000000000000000000000001",
                    "signature": [
                        "0x323d2b227ee23a4bc72f398040ae4f6005bcf907ecf8c90d43009d01c9f9e0d",
                        "0x7e8def72bc4d5e27ff1ada45640c38ee65a8feb2097546d3296d8d5272a3898",
                    ],
                    "nonce": "0x16",
                    "sender_address": "0x49c825710365f3cd0a8fa61e27368197b47727a4d0a78981cc2b19febaef9bd",
                    "calldata": [
                        "0x1",
                        "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
                        "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",
                        "0x0",
                        "0x3",
                        "0x3",
                        "0x1",
                        "0x1",
                        "0x0",
                    ],
                }
            ],
            ["SKIP_VALIDATE"],
        ]

    @staticmethod
    def _estimate_fee_params_factory(rng: RNG) -> dict[str, t.Any]:
        return {
            "request": [
                {
                    "type": "INVOKE",
                    "max_fee": "0x0",
                    "version": "0x100000000000000000000000000000001",
                    "signature": [
                        "0x323d2b227ee23a4bc72f398040ae4f6005bcf907ecf8c90d43009d01c9f9e0d",
                        "0x7e8def72bc4d5e27ff1ada45640c38ee65a8feb2097546d3296d8d5272a3898",
                    ],
                    "nonce": "0x9a9",
                    "sender_address": "0x49c825710365f3cd0a8fa61e27368197b47727a4d0a78981cc2b19febaef9bd",
                    "calldata": [
                        "0x1",
                        "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
                        "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",
                        "0x0",
                        "0x3",
                        "0x3",
                        "0x1",
                        "0x1",
                        "0x0",
                    ],
                }
            ],
            "block_id": {"block_number": rng.random.randint(368000, 368900)},
        }

    def _get_class_params_factory(self, rng: RNG) -> list[Account | str]:
        return ["latest", self.test_data.get_random_account(rng)]

    def _get_tx_hash_params_factory(self, rng: RNG) -> list[TxHash]:
        return [self.test_data.get_random_tx_hash(rng)]

    def _get_contract_address(self, rng: RNG) -> Account:
        return self.test_data.get_random_account(rng)
