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

from chainbench.user.tasks.common import expand_tasks
from chainbench.user.tasks.solana import SolanaMethods


class SolanaProfile(SolanaMethods):
    wait_time = constant_pacing(1)
    tasks = expand_tasks(
        {
            SolanaMethods.get_account_info_task: 1000,
            SolanaMethods.get_block_task: 175,
            SolanaMethods.get_token_accounts_by_owner_task: 150,
            SolanaMethods.get_multiple_accounts_task: 150,
            SolanaMethods.get_transaction_task: 130,
            SolanaMethods.get_signatures_for_address_task: 75,
            SolanaMethods.get_latest_blockhash_task: 75,
            SolanaMethods.get_balance_task: 75,
            SolanaMethods.get_slot_task: 20,
            SolanaMethods.get_block_height_task: 15,
            SolanaMethods.get_block_time_task: 15,
            SolanaMethods.get_program_accounts_task: 5,
            SolanaMethods.get_signature_statuses_task: 4,
            SolanaMethods.get_blocks_task: 2,
            SolanaMethods.get_epoch_info_task: 2,
        }
    )
