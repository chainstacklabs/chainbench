import json
import logging
import typing as t
from dataclasses import dataclass, field
from secrets import token_hex

import httpx
from configargparse import Namespace
from gevent.lock import Semaphore as GeventSemaphore
from tenacity import retry, stop_after_attempt

from chainbench.util.rng import RNG, get_rng

Account = str
Accounts = list[Account]
TxHash = str
TxHashes = list[TxHash]
Tx = dict[str, t.Any]
Txs = list[Tx]
Block = dict[str, t.Any]
BlockNumber = int
BlockHash = str
Blocks = list[tuple[BlockNumber, BlockHash]]
ChainId = int


@dataclass(frozen=True)
class BlockchainDataSize:
    blocks: int
    txs: int
    accounts: int


@dataclass(frozen=True)
class Sizes:
    XS = BlockchainDataSize(10, 100, 100)
    S = BlockchainDataSize(100, 1_000, 1_000)
    M = BlockchainDataSize(1_000, 10_000, 10_000)
    L = BlockchainDataSize(10_000, 100_000, 100_000)
    XL = BlockchainDataSize(100_000, 1_000_000, 1_000_000)

    @classmethod
    def get_size(cls, size: str) -> BlockchainDataSize:
        try:
            return getattr(cls, size.upper())
        except AttributeError:
            raise ValueError(f"Invalid size: '{size}'. Valid Sizes are S, M, L, XL")

    @classmethod
    def get_custom_size(cls, blocks: int, txs: int, accounts: int) -> BlockchainDataSize:
        return BlockchainDataSize(blocks, txs, accounts)


@dataclass
class BlockchainData:
    start_block_number: BlockNumber = 0
    end_block_number: BlockNumber = 0
    blocks: Blocks = field(default_factory=list)
    txs: Txs = field(default_factory=list)
    tx_hashes: TxHashes = field(default_factory=list)
    accounts: Accounts = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def from_json(self, json_data: str) -> None:
        data = json.loads(json_data)
        self.start_block_number = data["start_block_number"]
        self.end_block_number = data["end_block_number"]
        self.blocks = data["blocks"]
        self.txs = data["txs"]
        self.tx_hashes = data["tx_hashes"]
        self.accounts = data["accounts"]


class BaseTestData:
    DEFAULT_SIZE = "S"

    def __init__(self, rpc_version: str = "2.0"):
        self._logger = logging.getLogger(__name__)
        self._host: str | None = None
        self._client: httpx.Client = httpx.Client()
        self._rpc_version = rpc_version

        self._lock = GeventSemaphore()
        self._logger.debug("Locking")
        self._lock.acquire()
        self._logger.debug("Locked")

        self._data: BlockchainData | None = None

    def set_host(self, host_url: str):
        self._host = host_url
        self._logger.debug("Host: %s", self._host)

    def update(self, parsed_options: Namespace):
        self._logger.info("Updating data")
        self._data = self._get_init_data_from_blockchain(parsed_options)
        self._logger.info("Data fetched")
        self._logger.debug("Data: %s", self._data)
        self._logger.info("Data updated. Releasing lock")
        self._lock.release()
        self._logger.info("Lock released")

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
        raise NotImplementedError

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> tuple[BlockNumber, BlockNumber]:
        raise NotImplementedError

    # get initial data from blockchain
    def _get_init_data_from_blockchain(self, parsed_options: Namespace) -> BlockchainData:
        def print_progress():
            print(
                f"txs = {len(txs)}/{size.txs}  "
                f"accounts = {len(accounts)}/{size.accounts}  "
                f"blocks = {len(blocks)}/{size.blocks}",
                end="\r",
            )

        txs: list[Tx] = []
        tx_hashes: set[TxHash] = set()
        accounts: set[Account] = set()
        blocks: set[tuple[BlockNumber, BlockHash]] = set()
        start_block_number: BlockNumber
        end_block_number: BlockNumber
        return_txs: bool
        start_block_number, end_block_number = self._get_start_and_end_blocks(parsed_options)
        size_str = parsed_options.size.upper() if parsed_options.size != "None" else self.DEFAULT_SIZE
        size = Sizes.get_size(size_str)

        print(f"Test data size: {size_str}")
        self._logger.info(f"Test data size: {size_str}")

        while size.txs > len(txs) or size.accounts > len(accounts) or size.blocks > len(blocks):
            print_progress()
            if size.accounts > len(accounts) or size.txs > len(txs):
                return_txs = True
            else:
                return_txs = False
            block_number, block = self._fetch_random_block(start_block_number, end_block_number, return_txs)
            self._process_block(block_number, block, txs, tx_hashes, accounts, blocks, size, return_txs)
        else:
            print_progress()
            print("\n")  # new line after progress display upon exiting loop

        return BlockchainData(
            end_block_number=end_block_number,
            start_block_number=start_block_number,
            blocks=sorted(list(blocks)),
            txs=txs,
            tx_hashes=sorted(list(tx_hashes)),
            accounts=sorted(list(accounts)),
        )

    def init_data_from_json(self, json_data: str) -> None:
        self._data = BlockchainData()
        self._data.from_json(json_data)
        self._logger.info("Data updated. Releasing lock")
        self._lock.release()
        self._logger.info("Lock released")

    @property
    def initialized(self) -> bool:
        return self._data is not None

    @property
    def host(self) -> str:
        if self._host is None:
            raise ValueError("Host is not initialized")

        return self._host

    @property
    def data(self) -> BlockchainData:
        if self._data is None:
            raise ValueError("Data is not initialized")

        return self._data

    @staticmethod
    def _parse_hex_to_int(value: str) -> int:
        return int(value, 16)

    @staticmethod
    def _append_if_not_none(data: list | set, val: t.Any) -> None:
        if val is not None:
            if isinstance(data, list):
                data.append(val)
            elif isinstance(data, set):
                data.add(val)

    def _make_body(self, method: str, params: list[t.Any] | None = None) -> dict[str, t.Any]:
        if params is None:
            params = []

        return {
            "jsonrpc": self._rpc_version,
            "method": method,
            "params": params,
            "id": token_hex(8),
        }

    def _make_call(self, method: str, params: list[t.Any] | None = None) -> t.Any:
        if params is None:
            params = []

        response = self._client.post(
            self.host,
            json=self._make_body(method, params),
        )

        self._logger.debug(f"Making call to {self.host} with method {method} and params {params}")
        self._logger.debug(f"Response: {response.text}")

        response.raise_for_status()

        # check if response is json
        try:
            data = response.json()
        except ValueError:
            self._logger.error("Response is not json: %s", response.text)
            raise

        # check if response is error
        if "error" in data:
            self._logger.error("Response is error: %s", response.text)
            raise ValueError(response.text)

        # check if response is valid
        if "result" not in data:
            self._logger.error("Response is not valid: %s", response.text)
            raise ValueError(response.text)

        return data["result"]

    def close(self) -> None:
        self._client.close()

    def wait(self) -> None:
        self._lock.wait()

    def _fetch_block(self, block_number: BlockNumber, return_txs: bool = True) -> tuple[BlockNumber, Block]:
        raise NotImplementedError

    @retry(reraise=True, stop=stop_after_attempt(5))
    def _fetch_random_block(
        self,
        start: BlockNumber,
        end: BlockNumber,
        return_txs: bool = True,
    ) -> tuple[BlockNumber, Block]:
        rng = get_rng()
        block_number = rng.random.randint(start, end)
        return self._fetch_block(block_number, return_txs=return_txs)

    @staticmethod
    def get_random_bool(rng: RNG | None = None) -> bool:
        if rng is None:
            rng = get_rng()
        return rng.random.choice([True, False])

    def get_random_block_number(self, rng: RNG | None = None) -> BlockNumber:
        if rng is None:
            rng = get_rng()
        return rng.random.randint(self.start_block_number, self.end_block_number)

    def get_random_block_hash(self, rng: RNG | None = None) -> BlockHash:
        if rng is None:
            rng = get_rng()
        _, block_hash = rng.random.choice(self.blocks)
        return block_hash

    def get_random_tx_hash(self, rng: RNG | None = None) -> TxHash:
        if rng is None:
            rng = get_rng()
        return rng.random.choice(self.tx_hashes)

    def get_random_tx(self, rng: RNG | None = None) -> Tx:
        if rng is None:
            rng = get_rng()
        return rng.random.choice(self.txs)

    def get_random_recent_block_number(self, n: int, rng: RNG | None = None) -> BlockNumber:
        if rng is None:
            rng = get_rng()
        return rng.random.randint(
            self.end_block_number - n,
            self.end_block_number,
        )

    def get_random_account(self, rng: RNG | None = None) -> Account:
        if rng is None:
            rng = get_rng()
        return rng.random.choice(self.accounts)

    @property
    def start_block_number(self) -> BlockNumber:
        return self.data.start_block_number

    @property
    def end_block_number(self) -> BlockNumber:
        return self.data.end_block_number

    @property
    def txs(self) -> Txs:
        return self.data.txs

    @property
    def tx_hashes(self) -> TxHashes:
        return self.data.tx_hashes

    @property
    def accounts(self) -> Accounts:
        return self.data.accounts

    @property
    def blocks(self) -> Blocks:
        return self.data.blocks
