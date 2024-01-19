import json
import logging
import typing as t
from dataclasses import dataclass

from chainbench.util.rng import RNG, get_rng

from .blockchain import (
    Account,
    BlockHash,
    BlockNumber,
    BlockRange,
    RPCError,
    TestData,
    Tx,
    TxHash,
)
from .evm import EVMBlock

logger = logging.getLogger(__name__)

Slot = BlockNumber


@dataclass
class SolanaBlock(EVMBlock):
    block_height: BlockNumber

    @classmethod
    def from_response(cls, slot: Slot, data: dict[str, t.Any]):
        block_height = data["blockHeight"]
        block_hash: BlockHash = data["blockhash"]
        txs: list[Tx] = data["transactions"]
        tx_hashes: list[TxHash] = []
        accounts: set[Account] = set()
        for index, tx in enumerate(txs):
            if index == 100:
                # limit it to 100 per block
                break
            cls._append_if_not_none(txs, tx)
            cls._append_if_not_none(tx_hashes, tx["transaction"]["signatures"][0])
            for account in tx["transaction"]["accountKeys"]:
                if account["pubkey"] != "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    cls._append_if_not_none(accounts, account["pubkey"])
        return cls(slot, block_hash, txs, tx_hashes, list(accounts), block_height)


class SolanaTestData(TestData[SolanaBlock]):
    BLOCK_TIME = 0.4

    def get_block_from_data(self, data: dict[str, t.Any] | str) -> SolanaBlock:
        if isinstance(data, str):
            data_dict = json.loads(data)
        else:
            data_dict = data
        return SolanaBlock(**data_dict)

    def fetch_latest_block_number(self) -> Slot:
        slot = self.client.make_call("getLatestBlockhash")["context"]["slot"]
        return slot

    def fetch_block(self, slot: Slot) -> SolanaBlock:
        config_object = {
            "encoding": "json",
            "transactionDetails": "accounts",
            "rewards": False,
            "maxSupportedTransactionVersion": 0,
        }
        try:
            result = self.client.make_call("getBlock", [slot, config_object])
        except RPCError as e:
            self._logger.error(f"Failed to fetch block {slot}: {e.code} {e.message}")
            print(f"Failed to fetch block {slot}: {e.code} {e.message}")

            if e.code in [-32004, -32007, -32014]:
                # block not found
                return self.fetch_block(self.fetch_latest_block_number())
            else:
                raise e
        return SolanaBlock.from_response(slot, result)

    def _fetch_first_available_block(self) -> Slot:
        slot = self.client.make_call("getFirstAvailableBlock")
        return slot

    def _get_start_and_end_blocks(self, use_latest_blocks: bool) -> BlockRange:
        end_block_number = self.fetch_latest_block_number()
        earliest_available_block_number = self._fetch_first_available_block()

        # factor in run_time and add 10% buffer to ensure blocks used in test data are
        # not removed from the ledger
        earliest_available_block_number += int((self.parsed_options.run_time / self.BLOCK_TIME) * 1.1)
        start_block_number = earliest_available_block_number

        if use_latest_blocks:
            start_block_number = end_block_number - self.data.size.blocks_len + 1

        if start_block_number < earliest_available_block_number:
            raise ValueError(
                f"Earliest available block (with buffer) is {earliest_available_block_number}, "
                f"but start block is {start_block_number}"
            )

        return BlockRange(start_block_number, end_block_number)

    def get_random_block_hash(self, rng: RNG | None = None) -> BlockHash:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).block_hash

    def get_random_block_height(self, rng: RNG | None = None) -> BlockNumber:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).block_height

    def get_random_tx_hash(self, rng: RNG | None = None) -> TxHash:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).get_random_tx_hash(rng)

    def get_random_tx(self, rng: RNG | None = None) -> Tx:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).get_random_tx(rng)

    def get_random_block_range(self, n: int, rng: RNG | None = None) -> BlockRange:
        if rng is None:
            rng = get_rng()
        if n >= (self.end_block_number - self.start_block_number):
            end = rng.random.randint(self.end_block_number - n, self.end_block_number)
            return BlockRange(end - n, end)
        else:
            start = rng.random.randint(self.start_block_number, self.end_block_number - n)
            return BlockRange(start, start + n)

    def get_random_account(self, rng: RNG | None = None) -> Account:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).get_random_account(rng)
