from chainbench.test_data import Account, BlockNumber, SolanaTestData, TxHash
from chainbench.util.rng import RNG

from .http import JsonRpcUser


class SolanaUser(JsonRpcUser):
    abstract = True
    test_data = SolanaTestData()
    rpc_error_code_exclusions = [-32007]

    def _get_account_info_params_factory(self, rng: RNG) -> list[Account | dict]:
        return [self.test_data.get_random_account(rng), {"encoding": "jsonParsed"}]

    def _get_block_params_factory(self, rng: RNG) -> list[BlockNumber | dict]:
        return [
            self.test_data.get_random_block_number(rng),
            {
                "encoding": "jsonParsed",
                "transactionDetails": "full",
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

    def _get_balance_params_factory(self, rng: RNG) -> list[Account | dict]:
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
        end_number = start_number + rng.random.randint(1, 4)
        return [
            start_number,
            end_number,
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
