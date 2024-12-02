import base64
import re

from solders.message import Message

from chainbench.test_data import Account, BlockNumber, SolanaTestData, TxHash
from chainbench.user.jsonrpc import JrpcHttpUser
from chainbench.util.jsonrpc import RpcCall
from chainbench.util.rng import RNG, RNGManager


class SolanaBaseUser(JrpcHttpUser):
    abstract = True
    test_data = SolanaTestData()
    rng = RNGManager()
    rpc_error_code_exclusions = [-32007]

    def _create_random_transaction_message(self, rng: RNG) -> Message:
        import base58
        from solders.hash import Hash
        from solders.instruction import AccountMeta, Instruction
        from solders.pubkey import Pubkey

        receiver = Pubkey(base58.b58decode(self.test_data.get_random_account(rng)))
        sender = Pubkey(base58.b58decode(self.test_data.get_random_account(rng)))
        recent_blockhash = Hash(base58.b58decode(self.test_data.get_random_block_hash(rng)))

        receiver_account = AccountMeta(pubkey=receiver, is_signer=False, is_writable=True)
        sender_account = AccountMeta(pubkey=sender, is_signer=True, is_writable=True)

        inst = Instruction(
            program_id=Pubkey(base58.b58decode("11111111111111111111111111111111")),
            accounts=[sender_account, receiver_account],
            data=bytes([2, 0, 0, 0, 64, 66, 15, 0, 0, 0, 0, 0]),
        )
        msg = Message.new_with_blockhash(instructions=[inst], blockhash=recent_blockhash, payer=sender)
        return msg

    def _get_fee_for_message_params_factory(self, rng: RNG) -> list[str | dict]:
        base64_msg = base64.b64encode(bytes(self._create_random_transaction_message(rng))).decode()
        return [base64_msg, {"commitment": "confirmed"}]

    def _simulate_transaction_params_factory(self, rng: RNG) -> list[str | dict]:
        from solders.transaction import Transaction

        tx = Transaction.new_unsigned(self._create_random_transaction_message(rng))
        encoded_tx = base64.b64encode(bytes(tx)).decode()
        return [encoded_tx, {"commitment": "confirmed", "encoding": "base64"}]

    def _get_account_info_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [self.test_data.get_random_account(rng), {"encoding": "jsonParsed"}]

    def _get_block_params_factory(self, rng: RNG) -> list[BlockNumber | dict]:
        return [
            self.test_data.get_random_block_number(rng),
            {
                "encoding": "jsonParsed",
                "transactionDetails": "signatures",
                "maxSupportedTransactionVersion": 0,
            },
        ]

    def _get_token_accounts_by_owner_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [
            self.test_data.get_random_account(rng),
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"},
        ]

    def _get_multiple_accounts_params_factory(self, rng: RNG) -> list[list[Account] | dict]:
        return [
            [self.test_data.get_random_account(rng) for _ in range(2, 2 + rng.random.randint(0, 3))],
            {"encoding": "jsonParsed"},
        ]

    def _get_transaction_params_factory(self, rng: RNG) -> list[TxHash | dict]:
        return [
            self.test_data.get_random_tx_hash(rng),
            {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0},
        ]

    def _get_signatures_for_address_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [
            self.test_data.get_random_account(rng),
            {"limit": rng.random.randint(1, 10)},
        ]

    def _random_account_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [
            self.test_data.get_random_account(rng),
            {"commitment": "processed"},
        ]

    def _random_token_account_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [self.test_data.get_random_token_account(rng)]

    def _get_signature_statuses_params_factory(self, rng: RNG) -> list[list[TxHash] | dict]:
        return [
            [self.test_data.get_random_tx_hash(rng) for _ in range(2, 2 + rng.random.randint(0, 3))],
            {"searchTransactionHistory": True},
        ]

    def _get_blocks_params_factory(self, rng: RNG) -> list[BlockNumber | dict]:
        start_number = self.test_data.get_random_block_number(rng)
        end_number = start_number + rng.random.randint(20, 40)
        return [
            start_number,
            end_number,
            {"commitment": "confirmed"},
        ]

    def _get_blocks_with_limit_params_factory(self, rng: RNG) -> list[BlockNumber | dict]:
        end_number = self.test_data.get_random_block_number(rng)
        start_number = end_number - rng.random.randint(1, 20)
        block_len = end_number - start_number
        return [
            start_number,
            block_len,
            {"commitment": "confirmed"},
        ]

    def _get_confirmed_signatures_for_address2_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [
            self.test_data.get_random_account(rng),
            {
                "limit": rng.random.randint(1, 10),
                "commitment": "confirmed",
            },
        ]

    def _get_recent_prioritization_fees_params_factory(self, rng: RNG) -> list[list[str]]:
        accounts_len = rng.random.randint(1, 128)
        return [[self.test_data.get_random_account(rng) for _ in range(accounts_len)]]

    # TODO: Fix "Block XXX cleaned up, does not exist on node." error
    def _get_inflation_reward_params_factory(self, rng: RNG) -> list[list[str] | dict]:
        accounts_len = rng.random.randint(1, 10)
        return [
            [self.test_data.get_random_account(rng) for _ in range(accounts_len)],
            {"minContextSlot": self.test_data.get_random_block_number(rng)},
        ]

    @staticmethod
    def _get_program_accounts_params_factory() -> list[str | dict]:
        return [
            "Stake11111111111111111111111111111111111111",
            {
                "encoding": "jsonParsed",
                "commitment": "finalized",
                "filters": [{"memcmp": {"bytes": "2K9XJAj3VtojUhyKdXVfGnueSvnyFNfSACkn1CwgBees", "offset": 12}}],
            },
        ]

    @staticmethod
    def _get_recent_performance_samples_params_factory(rng: RNG) -> list[int]:
        return [rng.random.randint(1, 50)]

    def _get_slot_leaders_params_factory(self, rng: RNG) -> list[BlockNumber | dict]:
        end = self.test_data.get_random_block_number(rng)
        length = rng.random.randint(1, 10)
        start = end - length
        return [start, length]

    # TODO: Fix "Invalid param: not a stake account" error
    def _get_stake_activation_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [self.test_data.get_random_account(rng)]

    def _token_mint_pubkey_params_factory(self, rng: RNG) -> list[str]:
        return [self.test_data.get_random_token_address(rng)]

    def _get_token_accounts_by_delegate_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [
            self.test_data.get_random_account(rng),
            {
                "mint": self.test_data.get_random_token_address(rng),
            },
            {"encoding": "jsonParsed"},
        ]

    def _is_blockhash_valid_params_factory(self, rng: RNG) -> list[str | dict]:
        return [
            self.test_data.get_random_block_hash(rng),
            {"commitment": "processed"},
        ]


class SolanaRpcMethods(SolanaBaseUser):
    abstract = True

    def get_account_info(self) -> RpcCall:
        return RpcCall(
            method="getAccountInfo",
            params=self._get_account_info_params_factory(self.rng.get_rng()),
        )

    def get_balance(self) -> RpcCall:
        return RpcCall(
            method="getBalance",
            params=self._random_account_params_factory(self.rng.get_rng()),
        )

    def get_block(self) -> RpcCall:
        return RpcCall(
            method="getBlock",
            params=self._get_block_params_factory(self.rng.get_rng()),
        )

    def get_block_commitment(self) -> RpcCall:
        return RpcCall(
            method="getBlockCommitment",
            params=[
                self.test_data.get_random_block_number(self.rng.get_rng()),
            ],
        )

    @staticmethod
    def get_block_height() -> RpcCall:
        return RpcCall(
            method="getBlockHeight",
        )

    @staticmethod
    def get_block_production() -> RpcCall:
        return RpcCall(
            method="getBlockProduction",
        )

    def get_block_time(self) -> RpcCall:
        return RpcCall(
            method="getBlockTime",
            params=[
                self.test_data.get_random_block_number(self.rng.get_rng()),
            ],
        )

    def get_blocks(self) -> RpcCall:
        return RpcCall(
            method="getBlocks",
            params=self._get_blocks_params_factory(self.rng.get_rng()),
        )

    def get_blocks_with_limit(self) -> RpcCall:
        return RpcCall(
            method="getBlocksWithLimit",
            params=self._get_blocks_with_limit_params_factory(self.rng.get_rng()),
        )

    @staticmethod
    def get_cluster_nodes() -> RpcCall:
        return RpcCall(
            method="getClusterNodes",
        )

    @staticmethod
    def get_epoch_info() -> RpcCall:
        return RpcCall(
            method="getEpochInfo",
        )

    @staticmethod
    def get_epoch_schedule() -> RpcCall:
        return RpcCall(
            method="getEpochSchedule",
        )

    def get_fee_for_message(self) -> RpcCall:
        return RpcCall(
            method="getFeeForMessage",
            params=self._get_fee_for_message_params_factory(self.rng.get_rng()),
        )

    @staticmethod
    def get_first_available_block() -> RpcCall:
        return RpcCall(
            method="getFirstAvailableBlock",
        )

    @staticmethod
    def get_genesis_hash() -> RpcCall:
        return RpcCall(
            method="getGenesisHash",
        )

    @staticmethod
    def get_health() -> RpcCall:
        return RpcCall(
            method="getHealth",
        )

    @staticmethod
    def get_highest_snapshot_slot() -> RpcCall:
        return RpcCall(
            method="getHighestSnapshotSlot",
        )

    @staticmethod
    def get_identity() -> RpcCall:
        return RpcCall(
            method="getIdentity",
        )

    @staticmethod
    def get_inflation_governor() -> RpcCall:
        return RpcCall(
            method="getInflationGovernor",
        )

    @staticmethod
    def get_inflation_rate() -> RpcCall:
        return RpcCall(
            method="getInflationRate",
        )

    def get_inflation_reward(self) -> RpcCall:
        return RpcCall(
            method="getInflationReward",
            params=self._get_inflation_reward_params_factory(self.rng.get_rng()),
        )

    @staticmethod
    def get_largest_accounts() -> RpcCall:
        return RpcCall(
            method="getLargestAccounts",
        )

    @staticmethod
    def get_latest_blockhash() -> RpcCall:
        return RpcCall(method="getLatestBlockhash", params=[{"commitment": "processed"}])

    @staticmethod
    def get_leader_schedule() -> RpcCall:
        return RpcCall(
            method="getLeaderSchedule",
        )

    @staticmethod
    def get_max_retransmit_slot() -> RpcCall:
        return RpcCall(
            method="getMaxRetransmitSlot",
        )

    @staticmethod
    def get_max_shred_insert_slot() -> RpcCall:
        return RpcCall(
            method="getMaxShredInsertSlot",
        )

    def get_minimum_balance_for_rent_exemption(self) -> RpcCall:
        return RpcCall(
            method="getMinimumBalanceForRentExemption",
            params=[self.rng.get_rng().random.randint(1, 100)],
        )

    def get_multiple_accounts(self) -> RpcCall:
        return RpcCall(
            method="getMultipleAccounts",
            params=self._get_multiple_accounts_params_factory(self.rng.get_rng()),
        )

    def get_program_accounts(self) -> RpcCall:
        return RpcCall(
            method="getProgramAccounts",
            params=self._get_program_accounts_params_factory(),
        )

    def get_recent_performance_samples(self) -> RpcCall:
        return RpcCall(
            method="getRecentPerformanceSamples",
            params=self._get_recent_performance_samples_params_factory(self.rng.get_rng()),
        )

    def get_recent_prioritization_fees(self) -> RpcCall:
        return RpcCall(
            method="getRecentPrioritizationFees",
            params=self._get_recent_prioritization_fees_params_factory(self.rng.get_rng()),
        )

    def get_signature_statuses(self) -> RpcCall:
        return RpcCall(
            method="getSignatureStatuses",
            params=self._get_signature_statuses_params_factory(self.rng.get_rng()),
        )

    def get_signatures_for_address(self) -> RpcCall:
        return RpcCall(
            method="getSignaturesForAddress",
            params=self._get_signatures_for_address_params_factory(self.rng.get_rng()),
        )

    @staticmethod
    def get_slot() -> RpcCall:
        return RpcCall(
            method="getSlot",
        )

    @staticmethod
    def get_slot_leader() -> RpcCall:
        return RpcCall(
            method="getSlotLeader",
        )

    def get_slot_leaders(self) -> RpcCall:
        return RpcCall(
            method="getSlotLeaders",
            params=self._get_slot_leaders_params_factory(self.rng.get_rng()),
        )

    def get_stake_activation(self) -> RpcCall:
        return RpcCall(
            method="getStakeActivation",
            params=self._get_stake_activation_params_factory(self.rng.get_rng()),
        )

    @staticmethod
    def get_stake_minimum_delegation() -> RpcCall:
        return RpcCall(
            method="getStakeMinimumDelegation",
        )

    @staticmethod
    def get_supply() -> RpcCall:
        return RpcCall(
            method="getSupply",
        )

    def get_token_account_balance(self) -> RpcCall:
        return RpcCall(
            method="getTokenAccountBalance",
            params=self._random_token_account_params_factory(self.rng.get_rng()),
        )

    def get_token_accounts_by_delegate(self) -> RpcCall:
        return RpcCall(
            method="getTokenAccountsByDelegate",
            params=self._get_token_accounts_by_delegate_params_factory(self.rng.get_rng()),
        )

    def get_token_accounts_by_owner(self) -> RpcCall:
        return RpcCall(
            method="getTokenAccountsByOwner",
            params=self._get_token_accounts_by_owner_params_factory(self.rng.get_rng()),
        )

    def get_token_largest_accounts(self) -> RpcCall:
        return RpcCall(
            method="getTokenLargestAccounts",
            params=self._token_mint_pubkey_params_factory(self.rng.get_rng()),
        )

    def get_token_supply(self) -> RpcCall:
        return RpcCall(
            method="getTokenSupply",
            params=self._token_mint_pubkey_params_factory(self.rng.get_rng()),
        )

    def get_transaction(self) -> RpcCall:
        return RpcCall(
            method="getTransaction",
            params=self._get_transaction_params_factory(self.rng.get_rng()),
        )

    @staticmethod
    def get_transaction_count() -> RpcCall:
        return RpcCall(
            method="getTransactionCount",
        )

    @staticmethod
    def get_version() -> RpcCall:
        return RpcCall(
            method="getVersion",
        )

    @staticmethod
    def get_vote_accounts() -> RpcCall:
        return RpcCall(
            method="getVoteAccounts",
        )

    def is_blockhash_valid(self) -> RpcCall:
        return RpcCall(
            method="isBlockhashValid",
            params=self._is_blockhash_valid_params_factory(self.rng.get_rng()),
        )

    @staticmethod
    def minimum_ledger_slot() -> RpcCall:
        return RpcCall(
            method="minimumLedgerSlot",
        )

    def simulate_transaction(self) -> RpcCall:
        return RpcCall(
            method="simulateTransaction",
            params=self._simulate_transaction_params_factory(self.rng.get_rng()),
        )


class SolanaUser(SolanaRpcMethods):
    abstract = True

    @staticmethod
    def task_to_method(task_name: str) -> str:
        task_name_stripped = task_name.replace("_task", "")
        words = task_name_stripped.split("_")
        method = "".join([words[0]] + [word.capitalize() for word in words[1:]])
        return method

    @staticmethod
    def method_to_function_name(method: str):
        method_name_split = re.split("(?<=.)(?=[A-Z])", method)
        method_name = "_".join([word.lower() for word in method_name_split])
        return method_name

    def get_account_info_task(self) -> None:
        self.make_rpc_call(self.get_account_info())

    def get_balance_task(self) -> None:
        self.make_rpc_call(self.get_balance())

    def get_block_task(self) -> None:
        self.make_rpc_call(self.get_block())

    def get_block_commitment_task(self) -> None:
        self.make_rpc_call(self.get_block_commitment())

    def get_block_height_task(self) -> None:
        self.make_rpc_call(self.get_block_height())

    def get_block_production_task(self) -> None:
        self.make_rpc_call(self.get_block_production())

    def get_block_time_task(self) -> None:
        self.make_rpc_call(self.get_block_time())

    def get_blocks_task(self) -> None:
        self.make_rpc_call(self.get_blocks())

    def get_blocks_with_limit_task(self) -> None:
        self.make_rpc_call(self.get_blocks_with_limit())

    def get_cluster_nodes_task(self) -> None:
        self.make_rpc_call(self.get_cluster_nodes())

    def get_epoch_info_task(self) -> None:
        self.make_rpc_call(self.get_epoch_info())

    def get_epoch_schedule_task(self) -> None:
        self.make_rpc_call(self.get_epoch_schedule())

    def get_fee_for_message_task(self) -> None:
        self.make_rpc_call(self.get_fee_for_message())

    def get_first_available_block_task(self) -> None:
        self.make_rpc_call(self.get_first_available_block())

    def get_genesis_hash_task(self) -> None:
        self.make_rpc_call(self.get_genesis_hash())

    def get_health_task(self) -> None:
        self.make_rpc_call(self.get_health())

    def get_highest_snapshot_slot_task(self) -> None:
        self.make_rpc_call(self.get_highest_snapshot_slot())

    def get_identity_task(self) -> None:
        self.make_rpc_call(self.get_identity())

    def get_inflation_governor_task(self) -> None:
        self.make_rpc_call(self.get_inflation_governor())

    def get_inflation_rate_task(self) -> None:
        self.make_rpc_call(self.get_inflation_rate())

    def get_inflation_reward_task(self) -> None:
        self.make_rpc_call(self.get_inflation_reward())

    def get_largest_accounts_task(self) -> None:
        self.make_rpc_call(self.get_largest_accounts())

    def get_latest_blockhash_task(self) -> None:
        self.make_rpc_call(self.get_latest_blockhash())

    def get_leader_schedule_task(self) -> None:
        self.make_rpc_call(self.get_leader_schedule())

    def get_max_retransmit_slot_task(self) -> None:
        self.make_rpc_call(self.get_max_retransmit_slot())

    def get_max_shred_insert_slot_task(self) -> None:
        self.make_rpc_call(self.get_max_shred_insert_slot())

    def get_minimum_balance_for_rent_exemption_task(self) -> None:
        self.make_rpc_call(self.get_minimum_balance_for_rent_exemption())

    def get_multiple_accounts_task(self) -> None:
        self.make_rpc_call(self.get_multiple_accounts())

    def get_program_accounts_task(self) -> None:
        self.make_rpc_call(self.get_program_accounts())

    def get_recent_performance_samples_task(self) -> None:
        self.make_rpc_call(self.get_recent_performance_samples())

    def get_recent_prioritization_fees_task(self) -> None:
        self.make_rpc_call(self.get_recent_prioritization_fees())

    def get_signature_statuses_task(self) -> None:
        self.make_rpc_call(self.get_signature_statuses())

    def get_signatures_for_address_task(self) -> None:
        self.make_rpc_call(self.get_signatures_for_address())

    def get_slot_task(self) -> None:
        self.make_rpc_call(self.get_slot())

    def get_slot_leader_task(self) -> None:
        self.make_rpc_call(self.get_slot_leader())

    def get_slot_leaders_task(self) -> None:
        self.make_rpc_call(self.get_slot_leaders())

    def get_stake_activation_task(self) -> None:
        self.make_rpc_call(self.get_stake_activation())

    def get_stake_minimum_delegation_task(self) -> None:
        self.make_rpc_call(self.get_stake_minimum_delegation())

    def get_supply_task(self) -> None:
        self.make_rpc_call(self.get_supply())

    # TODO: Fix "Invalid param: not a Token account" and "Invalid param: could not find account" errors
    def get_token_account_balance_task(self) -> None:
        self.make_rpc_call(self.get_token_account_balance())

    def get_token_accounts_by_delegate_task(self) -> None:
        self.make_rpc_call(self.get_token_accounts_by_delegate())

    def get_token_accounts_by_owner_task(self) -> None:
        self.make_rpc_call(self.get_token_accounts_by_owner())

    def get_token_largest_accounts_task(self) -> None:
        self.make_rpc_call(self.get_token_largest_accounts())

    def get_token_supply_task(self) -> None:
        self.make_rpc_call(self.get_token_supply())

    def get_transaction_task(self) -> None:
        self.make_rpc_call(self.get_transaction())

    def get_transaction_count_task(self) -> None:
        self.make_rpc_call(self.get_transaction_count())

    def get_version_task(self) -> None:
        self.make_rpc_call(self.get_version())

    def get_vote_accounts_task(self) -> None:
        self.make_rpc_call(self.get_vote_accounts())

    def is_blockhash_valid_task(self) -> None:
        self.make_rpc_call(self.is_blockhash_valid())

    def minimum_ledger_slot_task(self) -> None:
        self.make_rpc_call(self.minimum_ledger_slot())

    def simulate_transaction_task(self) -> None:
        self.make_rpc_call(self.simulate_transaction())


class SolanaUserTest(SolanaUser):
    pass
