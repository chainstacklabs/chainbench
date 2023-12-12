import logging
from typing import Mapping

from chainbench.test_data.base import (
    Account,
    BaseTestData,
    Block,
    BlockchainDataSize,
    BlockHash,
    BlockNumber,
    ChainInfo,
    Tx,
    TxHash,
)

logger = logging.getLogger(__name__)


class EVMTestData(BaseTestData):
    CHAIN_INFO: Mapping[int, ChainInfo] = {
        1: {
            "name": "ethereum-mainnet",
            "start_block": 10000000,
        },
        56: {
            "name": "binance-smart-chain",
            "start_block": 20000000,
        },
        137: {
            "name": "polygon-mainnet",
            "start_block": 35000000,
        },
        26863: {
            "name": "oasis-mainnet",
            "start_block": 8000000,
        },
        43114: {
            "name": "avalanche-mainnet",
            "start_block": 20000000,
        },
        8453: {
            "name": "base-mainnet",
            "start_block": 1,
        },
        84531: {
            "name": "base-testnet",
            "start_block": 1,
        },
    }

    def _fetch_chain_id(self) -> int:
        return self._parse_hex_to_int(self._make_call("eth_chainId"))

    def _fetch_latest_block_number(self) -> int:
        result = self._make_call("eth_blockNumber")
        return self._parse_hex_to_int(result)

    def _fetch_block(self, block_number: int | str, return_txs: bool = True) -> tuple[BlockNumber, Block]:
        if isinstance(block_number, int):
            block_number = hex(block_number)
        elif (block_number := block_number.lower()) not in (
            "latest",
            "earliest",
            "pending",
        ):
            raise ValueError("Invalid block number")
        result = self._make_call("eth_getBlockByNumber", [block_number, return_txs])
        return self._parse_hex_to_int(result["number"]), result

    def _get_start_and_end_blocks(self, parsed_options) -> tuple[BlockNumber, BlockNumber]:
        chain_id: int = self._fetch_chain_id()
        end_block_number = self._fetch_latest_block_number()
        if not parsed_options.use_recent_blocks and chain_id in self.CHAIN_INFO:
            start_block_number = self.CHAIN_INFO[chain_id]["start_block"]
            logger.info("Using blocks from %s to %s as test data", start_block_number, end_block_number)
        else:
            start_block_number = end_block_number - 10000
            logger.info("Using recent blocks from %s to %s as test data", start_block_number, end_block_number)
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
    ):
        if size.blocks > len(blocks):
            self._append_if_not_none(blocks, (block_number, block["hash"]))
        if return_txs:
            for tx in block["transactions"]:
                if size.txs > len(txs):
                    self._append_if_not_none(txs, tx)
                    self._append_if_not_none(tx_hashes, tx["hash"])
                if size.accounts > len(accounts):
                    self._append_if_not_none(accounts, tx["from"])
                if size.accounts > len(accounts):
                    self._append_if_not_none(accounts, tx["to"])
