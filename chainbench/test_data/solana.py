import json
import logging
import typing as t
from argparse import Namespace
from dataclasses import dataclass

from tenacity import retry, stop_after_attempt

from chainbench.util.rng import RNG, get_rng

from ..util.http import JsonRpcError
from .blockchain import (
    Account,
    BlockHash,
    BlockNotFoundError,
    BlockNumber,
    BlockRange,
    InvalidBlockError,
    TestData,
    Tx,
    TxHash,
    append_if_not_none,
)
from .evm import EvmBlock

logger = logging.getLogger(__name__)

Slot = BlockNumber


@dataclass(frozen=True)
class SolanaBlock(EvmBlock):
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
            append_if_not_none(txs, tx)
            append_if_not_none(tx_hashes, tx["transaction"]["signatures"][0])
            for account in tx["transaction"]["accountKeys"]:
                if account["pubkey"] != "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    append_if_not_none(accounts, account["pubkey"])
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
        slot = self.client.make_rpc_call("getLatestBlockhash")["context"]["slot"]
        return slot

    def fetch_block(self, slot: Slot) -> SolanaBlock:
        config_object = {
            "encoding": "json",
            "transactionDetails": "accounts",
            "rewards": False,
            "maxSupportedTransactionVersion": 0,
        }
        try:
            result = self.client.make_rpc_call("getBlock", [slot, config_object])
        except JsonRpcError as e:
            self._logger.error(f"Failed to fetch block {slot}: {e.code} {e.message}")
            print(f"Failed to fetch block {slot}: {e.code} {e.message}")

            if e.code in [-32004, -32007, -32014]:
                # block not found
                raise BlockNotFoundError()
            else:
                raise e

        block = SolanaBlock.from_response(slot, result)
        if len(block.txs) == 0:
            raise InvalidBlockError
        return block

    @retry(reraise=True, stop=stop_after_attempt(5))
    def fetch_latest_block(self) -> SolanaBlock:
        return self.fetch_block(self.fetch_latest_block_number())

    def _fetch_first_available_block(self) -> Slot:
        slot = self.client.make_rpc_call("getFirstAvailableBlock")
        return slot

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> BlockRange:
        end_block_number = self.fetch_latest_block_number()
        earliest_available_block_number = self._fetch_first_available_block()

        # factor in run_time and add 10% buffer to ensure blocks used in test data are
        # not removed from the ledger
        earliest_available_block_number += int((parsed_options.run_time / self.BLOCK_TIME) * 1.1)
        start_block_number = earliest_available_block_number

        if parsed_options.use_latest_blocks:
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

    @staticmethod
    def get_random_token_address(self, rng: RNG | None = None) -> Account:
        if rng is None:
            rng = get_rng()
        token_addresses = [
            "z3dn17yLaGMKffVogeFHQ9zWVcXgqgf3PQnDsNs2g6M",  # Oxygen Protocol
            "2cZv8HrgcWSvC6n1uEiS48cEQGb1d3fiowP2rpa4wBL9",  # ACF Game
            "5fTwKZP2AK39LtFN9Ayppu6hdCVKfMGVm79F2EgHCtsi",  # WHEYO
            "NeonTjSjsuo3rexg9o6vHuMXw62f9V7zvmu8M8Zut44",  # Neon EVM
            "8BMzMi2XxZn9afRaMx5Z6fauk9foHXqV5cLTCYWRcVje",  # Staika
        ]
        return rng.random.choice(token_addresses)
