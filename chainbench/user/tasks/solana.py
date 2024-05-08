import re
import typing as t

from locust import task

from chainbench.user.solana import SolanaUser
from chainbench.util.rng import get_rng


class SolanaMethods(SolanaUser):
    abstract = True

    @staticmethod
    def task_to_method(task_name: str) -> str:
        task_name_stripped = task_name.replace("_task", "")
        words = task_name_stripped.split("_")
        method = "".join([words[0]] + [word.capitalize() for word in words[1:]])
        return method

    def method_to_task_function(self, method: str) -> t.Callable:
        method_name_split = re.split("(?<=.)(?=[A-Z])", method)
        method_name = "_".join([word.lower() for word in method_name_split])
        return getattr(self, f"{method_name}_task")

    # TODO: Separate out rpc_methods for Solana to allow for batch request support

    def get_account_info_task(self):
        self.make_rpc_call(
            method="getAccountInfo",
            params=self._get_account_info_params_factory(get_rng()),
        ),

    def get_balance_task(self):
        self.make_rpc_call(
            method="getBalance",
            params=self._random_account_params_factory(get_rng()),
        ),

    def get_block_task(self):
        self.make_rpc_call(
            method="getBlock",
            params=self._get_block_params_factory(get_rng()),
        ),

    def get_block_commitment_task(self) -> None:
        self.make_rpc_call(
            method="getBlockCommitment",
            params=[
                self.test_data.get_random_block_number(get_rng()),
            ],
        )

    def get_block_height_task(self) -> None:
        self.make_rpc_call(
            method="getBlockHeight",
        )

    def get_block_production_task(self) -> None:
        self.make_rpc_call(
            method="getBlockProduction",
        )

    def get_block_time_task(self) -> None:
        self.make_rpc_call(
            method="getBlockTime",
            params=[
                self.test_data.get_random_block_number(get_rng()),
            ],
        )

    def get_blocks_task(self) -> None:
        self.make_rpc_call(
            method="getBlocks",
            params=self._get_blocks_params_factory(get_rng()),
        )

    def get_blocks_with_limit_task(self) -> None:
        self.make_rpc_call(
            method="getBlocksWithLimit",
            params=self._get_blocks_with_limit_params_factory(get_rng()),
        )

    def get_cluster_nodes_task(self) -> None:
        self.make_rpc_call(
            method="getClusterNodes",
        )

    def get_epoch_info_task(self) -> None:
        self.make_rpc_call(
            method="getEpochInfo",
        )

    def get_epoch_schedule_task(self) -> None:
        self.make_rpc_call(
            method="getEpochSchedule",
        )

    def get_fee_for_message_task(self) -> None:
        self.make_rpc_call(
            method="getFeeForMessage",
            params=self._get_fee_for_message_params_factory(get_rng()),
        )

    def get_first_available_block_task(self) -> None:
        self.make_rpc_call(
            method="getFirstAvailableBlock",
        )

    def get_genesis_hash_task(self) -> None:
        self.make_rpc_call(
            method="getGenesisHash",
        )

    def get_health_task(self) -> None:
        self.make_rpc_call(
            method="getHealth",
        )

    def get_highest_snapshot_slot_task(self) -> None:
        self.make_rpc_call(
            method="getHighestSnapshotSlot",
        )

    def get_identity_task(self) -> None:
        self.make_rpc_call(
            method="getIdentity",
        )

    def get_inflation_governor_task(self) -> None:
        self.make_rpc_call(
            method="getInflationGovernor",
        )

    def get_inflation_rate_task(self) -> None:
        self.make_rpc_call(
            method="getInflationRate",
        )

    def get_inflation_reward_task(self) -> None:
        self.make_rpc_call(
            method="getInflationReward",
            params=self._get_inflation_reward_params_factory(get_rng()),
        )

    def get_largest_accounts_task(self) -> None:
        self.make_rpc_call(
            method="getLargestAccounts",
        )

    def get_latest_blockhash_task(self) -> None:
        self.make_rpc_call(method="getLatestBlockhash", params=[{"commitment": "processed"}])

    def get_leader_schedule_task(self) -> None:
        self.make_rpc_call(
            method="getLeaderSchedule",
        )

    def get_max_retransmit_slot_task(self) -> None:
        self.make_rpc_call(
            method="getMaxRetransmitSlot",
        )

    def get_max_shred_insert_slot_task(self) -> None:
        self.make_rpc_call(
            method="getMaxShredInsertSlot",
        )

    def get_minimum_balance_for_rent_exemption_task(self) -> None:
        self.make_rpc_call(
            method="getMinimumBalanceForRentExemption",
            params=[get_rng().random.randint(1, 100)],
        )

    def get_multiple_accounts_task(self) -> None:
        self.make_rpc_call(
            method="getMultipleAccounts",
            params=self._get_multiple_accounts_params_factory(get_rng()),
        )

    def get_program_accounts_task(self) -> None:
        self.make_rpc_call(
            method="getProgramAccounts",
            params=self._get_program_accounts_params_factory(),
        )

    def get_recent_performance_samples_task(self) -> None:
        self.make_rpc_call(
            method="getRecentPerformanceSamples",
            params=self._get_recent_performance_samples_params_factory(get_rng()),
        )

    def get_recent_prioritization_fees_task(self) -> None:
        self.make_rpc_call(
            method="getRecentPrioritizationFees",
            params=self._get_recent_prioritization_fees_params_factory(get_rng()),
        )

    def get_signature_statuses_task(self) -> None:
        self.make_rpc_call(
            method="getSignatureStatuses",
            params=self._get_signature_statuses_params_factory(get_rng()),
        )

    def get_signatures_for_address_task(self) -> None:
        self.make_rpc_call(
            method="getSignaturesForAddress",
            params=self._get_signatures_for_address_params_factory(get_rng()),
        )

    def get_slot_task(self) -> None:
        self.make_rpc_call(
            method="getSlot",
        )

    def get_slot_leader_task(self) -> None:
        self.make_rpc_call(
            method="getSlotLeader",
        )

    def get_slot_leaders_task(self) -> None:
        self.make_rpc_call(
            method="getSlotLeaders",
            params=self._get_slot_leaders_params_factory(get_rng()),
        )

    def get_stake_activation_task(self) -> None:
        self.make_rpc_call(
            method="getStakeActivation",
            params=self._get_stake_activation_params_factory(get_rng()),
        )

    def get_stake_minimum_delegation_task(self) -> None:
        self.make_rpc_call(
            method="getStakeMinimumDelegation",
        )

    def get_supply_task(self) -> None:
        self.make_rpc_call(
            method="getSupply",
        )

    # TODO: Fix "Invalid param: not a Token account" and "Invalid param: could not find account" errors
    def get_token_account_balance_task(self) -> None:
        self.make_rpc_call(
            method="getTokenAccountBalance",
            params=self._random_account_params_factory(get_rng()),
        )

    def get_token_accounts_by_delegate_task(self) -> None:
        self.make_rpc_call(
            method="getTokenAccountsByDelegate",
            params=self._get_token_accounts_by_delegate_params_factory(get_rng()),
        )

    def get_token_accounts_by_owner_task(self) -> None:
        self.make_rpc_call(
            method="getTokenAccountsByOwner",
            params=self._get_token_accounts_by_owner_params_factory(get_rng()),
        )

    def get_token_largest_accounts_task(self) -> None:
        self.make_rpc_call(
            method="getTokenLargestAccounts",
            params=self._token_mint_pubkey_params_factory(get_rng()),
        )

    def get_token_supply_task(self) -> None:
        self.make_rpc_call(
            method="getTokenSupply",
            params=self._token_mint_pubkey_params_factory(get_rng()),
        )

    def get_transaction_task(self) -> None:
        self.make_rpc_call(
            method="getTransaction",
            params=self._get_transaction_params_factory(get_rng()),
        )

    def get_transaction_count_task(self) -> None:
        self.make_rpc_call(
            method="getTransactionCount",
        )

    def get_version_task(self) -> None:
        self.make_rpc_call(
            method="getVersion",
        )

    def get_vote_accounts_task(self) -> None:
        self.make_rpc_call(
            method="getVoteAccounts",
        )

    def is_blockhash_valid_task(self) -> None:
        self.make_rpc_call(
            method="isBlockhashValid",
            params=self._is_blockhash_valid_params_factory(get_rng()),
        )

    def minimum_ledger_slot_task(self) -> None:
        self.make_rpc_call(
            method="minimumLedgerSlot",
        )

    def simulate_transaction_task(self) -> None:
        self.make_rpc_call(
            method="simulateTransaction",
            params=self._simulate_transaction_params_factory(get_rng()),
        )


class TestSolanaMethod(SolanaMethods):
    @task
    def run_task(self) -> None:
        self.method_to_task_function(self.environment.parsed_options.method)()
