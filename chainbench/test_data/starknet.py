import json
import logging
import typing as t

from .blockchain import (
    Account,
    BlockHash,
    BlockNumber,
    Tx,
    TxHash,
    append_if_not_none,
    parse_hex_to_int,
)
from .evm import ChainId, EvmBlock, EvmTestData

logger = logging.getLogger(__name__)


class StarkNetBlock(EvmBlock):
    @classmethod
    def from_response(cls, block_number: BlockNumber, data: dict[str, t.Any]):
        block_hash: BlockHash = data["block_hash"]
        txs: list[Tx] = data["transactions"]
        tx_hashes: list[TxHash] = []
        accounts: set[Account] = set()
        for index, tx in enumerate(txs):
            if index == 100:
                # limit it to 100 per block
                break
            append_if_not_none(tx_hashes, tx["transaction_hash"])
            append_if_not_none(txs, tx)
            try:
                append_if_not_none(accounts, tx["sender_address"])
            except KeyError:
                pass  # skip tx if it doesn't have sender_address
        return cls(block_number, block_hash, txs, tx_hashes, list(accounts))


class StarkNetTestData(EvmTestData):
    def get_block_from_data(self, data: dict[str, t.Any] | str) -> StarkNetBlock:
        if isinstance(data, str):
            data_dict: dict[str, t.Any] = json.loads(data)
        else:
            data_dict = data
        return StarkNetBlock(**data_dict)

    def fetch_chain_id(self) -> ChainId:
        return parse_hex_to_int(self.client.make_rpc_call("starknet_chainId"))

    def fetch_latest_block_number(self) -> BlockNumber:
        return self.client.make_rpc_call("starknet_blockNumber")

    def fetch_block(self, block_number: BlockNumber | str) -> StarkNetBlock:
        if isinstance(block_number, str) and (block_number := block_number.lower()) not in (
            "latest",
            "pending",
        ):
            raise ValueError("Invalid block number")
        params: dict[str, int] | str = {"block_number": block_number} if isinstance(block_number, int) else block_number

        result = self.client.make_rpc_call("starknet_getBlockWithTxs", [params])
        return StarkNetBlock.from_response(result["block_number"], result)
