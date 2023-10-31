"""
StarkNet profile.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "starknet_call" : 54
    "starket_chainId" : 25
    "starknet_getClassHashAt" : 17
    "starknet_getTransactionReceipt" : 3
    "Others" : 1
```
"""
from locust import constant_pacing, tag, task

from chainbench.user.starknet import StarkNetBenchUser
from chainbench.util.rng import get_rng


class StarkNetWalletProfile(StarkNetBenchUser):
    wait_time = constant_pacing(2)

    @task(435)
    def call_task(self):
        self.make_call(
            name="call",
            method="starknet_call",
            params=self._call_params_factory(get_rng())),

    @task(200)
    def chain_id_task(self):
        self.make_call(
            name="chain_id",
            method="starknet_chainId",
        ),

    @task(133)
    def get_class_hash_at_task(self):
        self.make_call(
            name="get_class_hash_at",
            method="starknet_getClassHashAt",
            params=self._get_class_params_factory(get_rng()),
        ),

    @task(21)
    def get_transaction_receipt_task(self):
        self.make_call(
            name="get_transaction_receipt",
            method="starknet_getTransactionReceipt",
            params=self._get_tx_hash_params_factory(get_rng()),
        ),

    @task(3)
    def get_class_at_task(self):
        self.make_call(
            name="get_class_at",
            method="starknet_getClassAt",
            params=self._get_class_params_factory(get_rng()),
        ),

    @task(3)
    def get_nonce_task(self):
        self.make_call(
            name="get_nonce",
            method="starknet_getNonce",
            params=["latest", self._get_contract_address(get_rng())],
        ),


    @task(2)
    def simulate_transaction_task(self):
        self.make_call(
            name="simulate_transaction",
            method="starknet_simulateTransaction",
            params=self._simulate_transaction_params_factory(get_rng()),
            url_postfix="/rpc/v0.3"
        ),

    @task(1)
    def estimate_fee_task(self):
        self.make_call(
            name="estimate_fee",
            method="starknet_estimateFee",
            params={
                "request": [
                    {
                        "type": "INVOKE",
                        "max_fee": "0x0",
                        "version": "0x100000000000000000000000000000001",
                        "signature": [
                            "0x323d2b227ee23a4bc72f398040ae4f6005bcf907ecf8c90d43009d01c9f9e0d",
                            "0x7e8def72bc4d5e27ff1ada45640c38ee65a8feb2097546d3296d8d5272a3898"
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
                        ]
                    }
                ],
                "block_id": "latest"
            }
        ),
