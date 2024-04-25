import base64

from solders.message import Message

from chainbench.test_data import Account, BlockNumber, SolanaTestData, TxHash
from chainbench.util.rng import RNG

from .http import JsonRpcUser


class SolanaUser(JsonRpcUser):
    abstract = True
    test_data = SolanaTestData()
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
