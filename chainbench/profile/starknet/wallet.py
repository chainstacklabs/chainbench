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

from locust import constant_pacing, task

from chainbench.user import StarkNetUser
from chainbench.util.rng import get_rng


class StarkNetWalletProfile(StarkNetUser):
    wait_time = constant_pacing(1)

    @task(435)
    def call_task(self):
        self.make_rpc_call(name="call", method="starknet_call", params=self._call_params_factory(get_rng())),

    @task(200)
    def chain_id_task(self):
        self.make_rpc_call(
            name="chain_id",
            method="starknet_chainId",
        ),

    @task(133)
    def get_class_hash_at_task(self):
        self.make_rpc_call(
            name="get_class_hash_at",
            method="starknet_getClassHashAt",
            params=self._get_class_params_factory(get_rng()),
        ),

    @task(21)
    def get_transaction_receipt_task(self):
        self.make_rpc_call(
            name="get_transaction_receipt",
            method="starknet_getTransactionReceipt",
            params=self._get_tx_hash_params_factory(get_rng()),
        ),

    @task(3)
    def get_class_at_task(self):
        self.make_rpc_call(
            name="get_class_at",
            method="starknet_getClassAt",
            params=self._get_class_params_factory(get_rng()),
        ),

    @task(3)
    def get_nonce_task(self):
        self.make_rpc_call(
            name="get_nonce",
            method="starknet_getNonce",
            params=["latest", self._get_contract_address(get_rng())],
        ),

    @task(2)
    def simulate_transaction_task(self):
        self.make_rpc_call(
            name="simulate_transaction",
            method="starknet_simulateTransaction",
            params=self._simulate_transaction_params_factory(get_rng()),
            path="/rpc/v0.3",
        ),

    @task(1)
    def estimate_fee_task(self):
        self.make_rpc_call(
            name="estimate_fee",
            method="starknet_estimateFee",
            params=self._estimate_fee_params_factory(get_rng()),
        ),
