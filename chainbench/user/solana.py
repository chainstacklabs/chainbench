from locust.contrib.fasthttp import RestResponseContextManager
from locust.exception import RescheduleTask

from chainbench.test_data import SolanaTestData
from chainbench.user.base import BaseBenchUser
from chainbench.util.rng import RNG


class SolanaBenchUser(BaseBenchUser):
    abstract = True
    test_data = SolanaTestData()

    def check_response(self, response: RestResponseContextManager, name: str):
        """Check the response for errors."""
        if response.status_code != 200:
            self.logger.info(f"Request failed with {response.status_code} code")
            self.logger.debug(
                f"Request to {response.url} failed with {response.status_code} code: {response.text}"  # noqa: E501
            )
            self.check_fatal(response)
            response.failure(f"Request failed with {response.status_code} code")
            response.raise_for_status()

        if response.request:
            self.logger.debug(f"Request: {response.request.body}")

        if response.js is None:
            self.logger.error(f"Response for {name}  is not a JSON: {response.text}")
            response.failure(f"Response for {name}  is not a JSON")
            raise RescheduleTask()

        if "jsonrpc" not in response.js:
            self.logger.error(f"Response for {name} is not a JSON-RPC: {response.text}")
            response.failure(f"Response for {name} is not a JSON-RPC")
            raise RescheduleTask()

        if "error" in response.js:
            self.logger.error(f"Response for {name} has a JSON-RPC error: {response.text}")
            if "code" in response.js["error"]:
                if response.js["error"]["code"] == -32007:
                    self.logger.warn(
                        f"Response for {name} has a JSON-RPC error: {response.js['error']['message']}"  # noqa: E501
                    )
                    return
                else:
                    self.logger.error(
                        f"Response for {name} has a JSON-RPC error {response.js['error']['code']}"  # noqa: E501
                    )
                    response.failure(
                        f"Response for {name} has a JSON-RPC error {response.js['error']['code']}"  # noqa: E501
                    )
                    raise RescheduleTask()
            response.failure("Unspecified JSON-RPC error")
            raise RescheduleTask()

        if not response.js.get("result"):
            self.logger.error(f"Response for {name} call has no result: {response.text}")

    def _get_account_info_params_factory(self, rng: RNG):
        return [self.test_data.get_random_account(rng), {"encoding": "jsonParsed"}]

    def _get_block_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_block_number(rng),
            {
                "encoding": "jsonParsed",
                "transactionDetails": "full",
                "maxSupportedTransactionVersion": 0,
            },
        ]

    def _get_token_accounts_by_owner_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_account(rng),
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"},
        ]

    def _get_multiple_accounts_params_factory(self, rng: RNG):
        return [
            [self.test_data.get_random_account(rng) for _ in range(2, 2 + rng.random.randint(0, 3))],
            {"encoding": "jsonParsed"},
        ]

    def _get_transaction_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_tx_hash(rng),
            {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0},
        ]

    def _get_signatures_for_address_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_account(rng),
            {"limit": rng.random.randint(1, 10)},
        ]

    def _get_balance_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_account(rng),
            {"commitment": "processed"},
        ]

    def _get_signature_statuses_params_factory(self, rng: RNG):
        return [
            [self.test_data.get_random_tx_hash(rng) for _ in range(2, 2 + rng.random.randint(0, 3))],
            {"searchTransactionHistory": True},
        ]

    def _get_blocks_params_factory(self, rng: RNG):
        start_number = self.test_data.get_random_block_number(rng)
        end_number = start_number + rng.random.randint(1, 4)
        return [
            start_number,
            end_number,
            {"commitment": "confirmed"},
        ]

    def _get_confirmed_signatures_for_address2_params_factory(self, rng: RNG):
        return [
            self.test_data.get_random_account(rng),
            {
                "limit": rng.random.randint(1, 10),
                "commitment": "confirmed",
            },
        ]
