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

from locust import constant_pacing

from chainbench.user.protocol.solana import SolanaUser


class SolanaProfile(SolanaUser):
    wait_time = constant_pacing(1)
    rpc_calls = {
        SolanaUser.get_account_info: 1000,
        SolanaUser.get_block: 175,
        SolanaUser.get_token_accounts_by_owner: 150,
        SolanaUser.get_multiple_accounts: 150,
        SolanaUser.get_transaction: 130,
        SolanaUser.get_signatures_for_address: 75,
        SolanaUser.get_latest_blockhash: 75,
        SolanaUser.get_balance: 75,
        SolanaUser.get_slot: 20,
        SolanaUser.get_block_height: 15,
        SolanaUser.get_block_time: 15,
        SolanaUser.get_program_accounts: 5,
        SolanaUser.get_signature_statuses: 4,
        SolanaUser.get_blocks: 2,
        SolanaUser.get_epoch_info: 2,
    }

    tasks = SolanaUser.expand_tasks(rpc_calls)
