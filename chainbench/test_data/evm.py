import logging
from typing import Mapping

from chainbench.test_data.base import BaseTestData, BlockchainData, Blocks, ChainInfo
from chainbench.util.rng import get_rng

logger = logging.getLogger(__name__)


class EVMTestData(BaseTestData):
    TXS_REQUIRED = 100
    ACCOUNTS_REQUIRED = 200
    SAVE_BLOCKS = 20

    CHAIN_INFO: Mapping[int, ChainInfo] = {
        1: {
            "name": "ethereum-mainnet",
            "start_block": 10000000,
            "end_block": 17000000,
        },
        56: {
            "name": "binance-smart-chain",
            "start_block": 20000000,
            "end_block": 29000000,
        },
        137: {
            "name": "polygon-mainnet",
            "start_block": 35000000,
            "end_block": 45000000,
        },
        26863: {
            "name": "oasis-mainnet",
            "start_block": 8000000,
            "end_block": 14000000,
        },
        43114: {
            "name": "avalanche-mainnet",
            "start_block": 20000000,
            "end_block": 32000000,
        },
        8453: {
            "name": "base-mainnet",
            "start_block": 1,
            "end_block": 2400000,
        },
        84531: {
            "name": "base-testnet",
            "start_block": 1,
            "end_block": 8200000,
        },
    }

    def _fetch_chain_id(self) -> int:
        return self._parse_hex_to_int(self._make_call("eth_chainId"))

    def _fetch_latest_block_number(self) -> int:
        result = self._make_call("eth_blockNumber")
        return self._parse_hex_to_int(result)

    def _fetch_block(self, block_number: int | str, return_txs: bool = True) -> tuple[int, dict]:
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

    def _fetch_random_block(self, start, end, return_txs=True) -> tuple[int, dict]:
        rng = get_rng()
        block_number = rng.random.randint(start, end)
        return self._fetch_block(block_number, return_txs=return_txs)

    def _get_start_and_end_blocks(self, use_recent_blocks: bool) -> tuple[int, int]:
        chain_id: int = self._fetch_chain_id()
        if not use_recent_blocks and chain_id in self.CHAIN_INFO:
            start_block_number = self.CHAIN_INFO[chain_id]["start_block"]
            end_block_number = self.CHAIN_INFO[chain_id]["end_block"]
            logger.info("Using blocks from %s to %s as test data", start_block_number, end_block_number)
            return start_block_number, end_block_number
        else:
            end_block_number = self._fetch_latest_block_number()
            start_block_number = end_block_number - 10000
            logger.info("Using recent blocks from %s to %s as test data", start_block_number, end_block_number)
            return start_block_number, end_block_number

    # get initial data from blockchain
    def _get_init_data(self, parsed_options) -> BlockchainData:
        txs: list[dict] = []
        tx_hashes: list[str] = []
        accounts: set[str] = set()
        blocks: Blocks = []
        start_block_number: int
        end_block_number: int
        return_txs: bool
        start_block_number, end_block_number = self._get_start_and_end_blocks(parsed_options.use_recent_blocks)

        while self.TXS_REQUIRED > len(txs) or self.ACCOUNTS_REQUIRED > len(accounts) or self.SAVE_BLOCKS > len(blocks):
            print(
                f"txs = {len(txs)}/{self.TXS_REQUIRED}  "
                f"accounts = {len(accounts)}/{self.ACCOUNTS_REQUIRED}  "
                f"blocks = {len(blocks)}/{self.SAVE_BLOCKS}"
            )
            if self.ACCOUNTS_REQUIRED > len(accounts) or self.TXS_REQUIRED > len(txs):
                return_txs = True
            else:
                return_txs = False
            block_number, block = self._fetch_random_block(start_block_number, end_block_number, return_txs)
            if self.SAVE_BLOCKS > len(blocks):
                blocks.append((block_number, block["hash"]))
            for tx in block["transactions"]:
                if self.TXS_REQUIRED > len(txs):
                    self._append_if_not_none(txs, tx)
                    self._append_if_not_none(tx_hashes, tx["hash"])
                if self.ACCOUNTS_REQUIRED > len(accounts):
                    self._append_if_not_none(accounts, tx["from"])
                if self.ACCOUNTS_REQUIRED > len(accounts):
                    self._append_if_not_none(accounts, tx["to"])

        return BlockchainData(
            end_block_number=end_block_number,
            start_block_number=start_block_number,
            blocks=blocks,
            txs=txs,
            tx_hashes=tx_hashes,
            accounts=sorted(list(accounts)),
        )
