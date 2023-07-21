from tenacity import retry, stop_after_attempt

from chainbench.test_data.base import BaseTestData, Block, BlockchainData
from chainbench.util.rng import get_rng


class SolanaTestData(BaseTestData):
    TXS_REQUIRED = 100
    ACCOUNTS_REQUIRED = 200
    BLOCK_TIME = 0.4

    def _fetch_block(self, block_number: int, return_txs: bool = True) -> dict:
        if return_txs:
            transaction_details = "accounts"
        else:
            transaction_details = "none"
        config_object = {
            "encoding": "json",
            "transactionDetails": transaction_details,
            "rewards": False,
            "maxSupportedTransactionVersion": 0,
        }
        try:
            result = self._make_call("getBlock", [block_number, config_object])
        except Exception as e:
            self._logger.error(f"Failed to fetch block {block_number}: {e}")
            raise e
        return result

    @retry(reraise=True, stop=stop_after_attempt(5))
    def _fetch_random_block(self, start, end, return_txs=True) -> dict:
        rng = get_rng()
        block_number = rng.random.randint(start, end)
        block = self._fetch_block(block_number, return_txs=return_txs)
        return block

    def _fetch_latest_slot_number(self):
        slot = self._make_call("getLatestBlockhash")["context"]["slot"]
        return slot

    @retry(reraise=True, stop=stop_after_attempt(5))
    def _fetch_latest_block(self):
        slot_number = self._fetch_latest_slot_number()
        latest_block = self._fetch_block(slot_number, return_txs=True)
        return slot_number, latest_block

    def _fetch_first_available_block(self):
        block = self._make_call("getFirstAvailableBlock")
        return block

    # get initial data from blockchain
    def _get_init_data(self, parsed_options) -> BlockchainData:
        txs: list[dict] = []
        tx_hashes: list[str] = []
        accounts: set[str] = set()
        blocks: list[Block] = []
        end_block_number, _latest_block = self._fetch_latest_block()
        start_block_number = self._fetch_first_available_block()

        # factor in run_time and add 10% buffer to ensure blocks used in test data are
        # not removed from the ledger
        start_block_number += int((parsed_options.run_time / self.BLOCK_TIME) * 1.1)

        while self.TXS_REQUIRED > len(txs) or self.ACCOUNTS_REQUIRED > len(accounts):
            if self.ACCOUNTS_REQUIRED > len(accounts) or self.TXS_REQUIRED > len(blocks):
                return_txs = True
            else:
                return_txs = False
            block = self._fetch_random_block(start_block_number, end_block_number, return_txs)
            for tx in block["transactions"]:
                if self.TXS_REQUIRED > len(txs):
                    self._append_if_not_none(txs, tx)
                    self._append_if_not_none(tx_hashes, tx["transaction"]["signatures"][0])
                    for account in tx["transaction"]["accountKeys"]:
                        if (
                            self.ACCOUNTS_REQUIRED > len(accounts)
                            and account["pubkey"] != "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                        ):
                            self._append_if_not_none(accounts, account["pubkey"])
                        else:
                            break

        return BlockchainData(
            end_block_number=end_block_number,
            start_block_number=start_block_number,
            blocks=[],
            txs=txs,
            tx_hashes=tx_hashes,
            accounts=sorted(list(accounts)),
        )
