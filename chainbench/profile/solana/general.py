"""
Solana profile.

Chart:
```mermaid
%%{init: {'theme':'forest'}}%%
pie title Methods Distribution
    "getAccountInfo" : 53
    "getBlock" : 9
    "getTokenAccountsByOwner" : 8
    "getMultipleAccounts" : 8
    "getTransaction" : 7
    "getSignaturesForAddress" : 4
    "getLatestBlockhash" : 4
    "getBalance" : 4
    "Others" : 3
```
"""
from locust import constant_pacing, tag, task

from chainbench.user import SolanaUser
from chainbench.util.rng import get_rng


class SolanaProfile(SolanaUser):
    wait_time = constant_pacing(1)

    @task(1000)
    def get_account_info_task(self):
        self.make_rpc_call(
            method="getAccountInfo",
            params=self._get_account_info_params_factory(get_rng()),
        ),

    @task(175)
    def get_block_task(self):
        self.make_rpc_call(
            method="getBlock",
            params=self._get_block_params_factory(get_rng()),
        ),

    @task(150)
    def get_token_accounts_by_owner(self):
        self.make_rpc_call(
            method="getTokenAccountsByOwner",
            params=self._get_token_accounts_by_owner_params_factory(get_rng()),
        ),

    @task(150)
    def get_multiple_accounts(self):
        self.make_rpc_call(
            method="getMultipleAccounts",
            params=self._get_multiple_accounts_params_factory(get_rng()),
        ),

    @task(130)
    def get_transaction(self):
        self.make_rpc_call(
            method="getTransaction",
            params=self._get_transaction_params_factory(get_rng()),
        ),

    @task(75)
    def get_signatures_for_address(self):
        self.make_rpc_call(
            method="getSignaturesForAddress",
            params=self._get_signatures_for_address_params_factory(get_rng()),
        ),

    @task(75)
    def get_latest_blockhash(self):
        self.make_rpc_call(
            method="getLatestBlockhash",
        ),

    @task(75)
    def get_balance(self):
        self.make_rpc_call(
            method="getBalance",
            params=self._get_balance_params_factory(get_rng()),
        ),

    @task(20)
    def get_slot(self):
        self.make_rpc_call(
            method="getSlot",
        ),

    @task(15)
    def get_block_height(self):
        self.make_rpc_call(
            method="getBlockHeight",
        ),

    @task(5)
    @tag("get-program-accounts")
    def get_program_accounts(self):
        self.make_rpc_call(
            method="getProgramAccounts",
            params=[
                "SharkXwkS3h24fJ2LZvgG5tPbsH3BKQYuAtKdqskf1f",
                {"encoding": "base64", "commitment": "confirmed"},
            ],
        ),

    @task(4)
    def get_signature_statuses(self):
        self.make_rpc_call(
            method="getSignatureStatuses",
            params=self._get_signature_statuses_params_factory(get_rng()),
        ),

    @task(3)
    def get_recent_blockhash(self):
        self.make_rpc_call(
            method="getRecentBlockhash",
        ),

    @task(2)
    def get_blocks(self):
        self.make_rpc_call(
            method="getBlocks",
            params=self._get_blocks_params_factory(get_rng()),
        ),

    @task(2)
    def get_epoch_info(self):
        self.make_rpc_call(
            method="getEpochInfo",
        ),

    @task(2)
    def get_confirmed_signatures_for_address2(self):
        self.make_rpc_call(
            method="getConfirmedSignaturesForAddress2",
            params=self._get_confirmed_signatures_for_address2_params_factory(get_rng()),
        ),
