import logging
from typing import Mapping

from chainbench.test_data import EVMTestData
from chainbench.test_data.base import BlockchainData, Blocks, ChainInfo
from chainbench.util.rng import get_rng

logger = logging.getLogger(__name__)


class StarkNetTestData(EVMTestData):
    TXS_REQUIRED = 100
    ACCOUNTS_REQUIRED = 200
    SAVE_BLOCKS = 20

    CHAIN_INFO: Mapping[int, ChainInfo] = {
        23448594291968334: {
            "name": "starknet-mainnet",
            "start_block": 100000,
            "end_block": 360000,
        },
        1536727068981429685321: {
            "name": "starknet-testnet",
            "start_block": 500000,
            "end_block": 890000,
        },
        393402129659245999442226: {
            "name": "starknet-testnet2",
            "start_block": 1,
            "end_block": 149000,
        }
    }

    def _fetch_chain_id(self) -> int:
        return self._parse_hex_to_int(self._make_call("starknet_chainId"))

    def _fetch_latest_block_number(self) -> int:
        result = self._make_call("starknet_blockNumber")
        return self._parse_hex_to_int(result)

    def _fetch_block(self, block_number: int | str, return_txs: bool = True) -> tuple[int, dict]:
        if isinstance(block_number, str) and (block_number := block_number.lower()) not in (
            "latest",
            "pending",
        ):
            raise ValueError("Invalid block number")
        params = {"block_number": block_number} if isinstance(block_number, int) else block_number

        result = self._make_call("starknet_getBlockWithTxs", [params])
        return result["block_number"], result

    def _fetch_random_block(self, start, end, return_txs=True) -> tuple[int, dict]:
        rng = get_rng()
        block_number = rng.random.randint(start, end)
        return self._fetch_block(block_number, return_txs=return_txs)

    # get initial data from blockchain
    def _get_init_data(self, parsed_options) -> BlockchainData:
        txs: list[dict] = []
        tx_hashes: list[str] = []
        accounts: set[str] = set()
        blocks: Blocks = []
        start_block_number: int
        end_block_number: int
        start_block_number, end_block_number = self._get_start_and_end_blocks(parsed_options.use_recent_blocks)

        while self.TXS_REQUIRED > len(txs) or self.ACCOUNTS_REQUIRED > len(accounts) or self.SAVE_BLOCKS > len(blocks):
            block_number, block = self._fetch_random_block(start_block_number, end_block_number)
            if self.SAVE_BLOCKS > len(blocks):
                blocks.append((block_number, block["block_hash"]))
            for tx in block["transactions"]:
                if self.TXS_REQUIRED > len(txs):
                    self._append_if_not_none(txs, tx)
                    self._append_if_not_none(tx_hashes, tx["transaction_hash"])
                if self.ACCOUNTS_REQUIRED > len(accounts):
                    try:
                        self._append_if_not_none(accounts, tx["sender_address"])
                    except KeyError:
                        pass    # skip tx if it doesn't have sender_address

        return BlockchainData(
            end_block_number=end_block_number,
            start_block_number=start_block_number,
            blocks=blocks,
            txs=txs,
            tx_hashes=tx_hashes,
            accounts=sorted(list(accounts)),
        )
