import logging

from configargparse import Namespace

from chainbench.test_data.base import (
    Account,
    BaseTestData,
    Block,
    BlockchainDataSize,
    BlockHash,
    BlockNumber,
    ChainId,
    Tx,
    TxHash,
)
from chainbench.test_data.blockchain.evm import ChainInfo, ERC20Contract
from chainbench.util.rng import RNG

logger = logging.getLogger(__name__)


class EVMTestData(BaseTestData):
    def __init__(self, rpc_version: str = "2.0"):
        super().__init__(rpc_version)
        self.chain_info: ChainInfo | None = None

    def set_chain_info(self, chain_id: ChainId):
        self.chain_info = ChainInfo(chain_id)

    def get_random_erc20_contract(self, rng: RNG) -> ERC20Contract:
        if self.chain_info is None:
            raise ValueError("Chain info is not set")
        else:
            return self.chain_info.get_random_contract(rng)

    def fetch_chain_id(self) -> int:
        return self._parse_hex_to_int(self._make_call("eth_chainId"))

    def _fetch_latest_block_number(self) -> BlockNumber:
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

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> tuple[BlockNumber, BlockNumber]:
        end_block_number = self._fetch_latest_block_number()
        if not parsed_options.use_recent_blocks and self.chain_info is not None:
            start_block_number = self.chain_info.start_block
            logger.info("Using blocks from %s to %s as test data", start_block_number, end_block_number)
        else:
            start_block_number = end_block_number - 128
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
    ) -> None:
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
