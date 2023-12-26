import logging
import typing as t
from typing import Mapping

from chainbench.test_data import EVMTestData
from chainbench.test_data.base import (
    Account,
    Block,
    BlockchainDataSize,
    BlockHash,
    BlockNumber,
    Tx,
    TxHash,
)

logger = logging.getLogger(__name__)


class ChainInfo(t.TypedDict):
    name: str
    start_block: BlockNumber


class StarkNetTestData(EVMTestData):
    CHAIN_INFO: Mapping[int, ChainInfo] = {
        23448594291968334: {
            "name": "starknet-mainnet",
            "start_block": 100000,
        },
        # TODO: uncomment after adding testnet support to methods like call, simulateTransaction, etc.
        # 1536727068981429685321: {
        #     "name": "starknet-testnet",
        #     "start_block": 500000,
        # },
        # 393402129659245999442226: {
        #     "name": "starknet-testnet2",
        #     "start_block": 1,
        # },
    }

    def fetch_chain_id(self) -> int:
        return self._parse_hex_to_int(self._make_call("starknet_chainId"))

    def _fetch_latest_block_number(self) -> BlockNumber:
        result = self._make_call("starknet_blockNumber")
        return result

    def _fetch_block(self, block_number: BlockNumber | str, return_txs: bool = True) -> tuple[BlockNumber, Block]:
        if isinstance(block_number, str) and (block_number := block_number.lower()) not in (
            "latest",
            "pending",
        ):
            raise ValueError("Invalid block number")
        params = {"block_number": block_number} if isinstance(block_number, int) else block_number

        if return_txs:
            result = self._make_call("starknet_getBlockWithTxs", [params])
        else:
            result = self._make_call("starknet_getBlockWithTxHashes", [params])
        return result["block_number"], result

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
            self._append_if_not_none(blocks, (block_number, block["block_hash"]))
        if return_txs:
            for tx in block["transactions"]:
                if size.txs > len(txs):
                    self._append_if_not_none(txs, tx)
                    self._append_if_not_none(tx_hashes, tx["transaction_hash"])
                if size.accounts > len(accounts):
                    try:
                        self._append_if_not_none(accounts, tx["sender_address"])
                    except KeyError:
                        pass  # skip tx if it doesn't have sender_address
