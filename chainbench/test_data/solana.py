import logging

from configargparse import Namespace
from tenacity import retry, stop_after_attempt

from chainbench.test_data.base import (
    Account,
    BaseTestData,
    Block,
    BlockchainDataSize,
    BlockHash,
    BlockNumber,
    Tx,
    TxHash,
)

logger = logging.getLogger(__name__)


class SolanaTestData(BaseTestData):
    BLOCK_TIME = 0.4

    def _fetch_block(self, block_number: BlockNumber, return_txs: bool = True) -> tuple[BlockNumber, Block]:
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
        return block_number, result

    def _fetch_latest_slot_number(self) -> BlockNumber:
        slot = self._make_call("getLatestBlockhash")["context"]["slot"]
        return slot

    @retry(reraise=True, stop=stop_after_attempt(5))
    def _fetch_latest_block(self) -> tuple[BlockNumber, Block]:
        slot_number = self._fetch_latest_slot_number()
        latest_block_number, latest_block = self._fetch_block(slot_number, return_txs=True)
        return latest_block_number, latest_block

    def _fetch_first_available_block(self) -> BlockNumber:
        block_number = self._make_call("getFirstAvailableBlock")
        return block_number

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> tuple[BlockNumber, BlockNumber]:
        end_block_number, _latest_block = self._fetch_latest_block()
        start_block_number = self._fetch_first_available_block()

        # factor in run_time and add 10% buffer to ensure blocks used in test data are
        # not removed from the ledger
        start_block_number += int((parsed_options.run_time / self.BLOCK_TIME) * 1.1)

        return start_block_number, end_block_number

    def _process_block(
        self,
        block_number: BlockNumber,
        block: Block,
        txs: list[Tx],
        tx_hashes: set[TxHash],
        accounts: set[Account],
        blocks: set[tuple[BlockNumber, BlockHash]],
        size: BlockchainDataSize,
        return_txs: bool = True,
    ) -> None:
        if size.blocks > len(blocks):
            self._append_if_not_none(blocks, (block_number, block["blockhash"]))
        if return_txs:
            for tx in block["transactions"]:
                if size.txs > len(txs):
                    self._append_if_not_none(txs, tx)
                    self._append_if_not_none(tx_hashes, tx["transaction"]["signatures"][0])
                    for account in tx["transaction"]["accountKeys"]:
                        if (
                            size.accounts > len(accounts)
                            and account["pubkey"] != "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                        ):
                            self._append_if_not_none(accounts, account["pubkey"])
