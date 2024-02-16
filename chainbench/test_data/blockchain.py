import json
import logging
import typing as t
from argparse import Namespace
from dataclasses import dataclass

from gevent.lock import Semaphore as GeventSemaphore
from tenacity import retry, stop_after_attempt

from chainbench.util.http import HttpClient
from chainbench.util.rng import RNG, get_rng

logger = logging.getLogger(__name__)

Account = str
TxHash = str
Tx = dict[str, t.Any]
BlockNumber = int
BlockHash = str


def parse_hex_to_int(value: str) -> int:
    return int(value, 16)


def append_if_not_none(data: list | set, val: t.Any) -> None:
    if val is not None:
        if isinstance(data, list):
            data.append(val)
        elif isinstance(data, set):
            data.add(val)


class BlockNotFoundError(Exception):
    # Raised when a block is not found for chains where slots can be empty
    pass


class InvalidBlockError(Exception):
    # Raised when a block has empty data or is otherwise invalid
    pass


@dataclass(frozen=True)
class Block:
    block_number: BlockNumber

    def to_json(self) -> str:
        return json.dumps(self.__dict__)


@dataclass
class BlockRange:
    start: BlockNumber
    end: BlockNumber

    def get_random_block_number(self, rng: RNG) -> BlockNumber:
        return rng.random.randint(self.start, self.end)


@dataclass
class Size:
    label: str
    blocks_len: int


@dataclass(frozen=True)
class Sizes:
    XS = Size("XS", 10)
    S = Size("S", 100)
    M = Size("M", 1_000)
    L = Size("L", 10_000)
    XL = Size("XL", 100_000)

    @classmethod
    def get_size(cls, size: str) -> Size:
        try:
            return getattr(cls, size.upper())
        except AttributeError:
            raise ValueError(f"Invalid size: '{size}'. Valid Sizes are XS, S, M, L, XL")


B = t.TypeVar("B", bound=Block)


class BlockchainData(t.Generic[B]):
    def __init__(self, size: Size, start: BlockNumber = 0, end: BlockNumber = 0):
        self.size = size
        self.block_range = BlockRange(start, end)
        self.blocks: list[B] = []
        self.block_numbers: list[BlockNumber] = []

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def push_block(self, block: B) -> None:
        if block.block_number in self.block_numbers:
            logger.warning(f"Block {block.block_number} already exists in the data")
        self.blocks.append(block)
        self.block_numbers.append(block.block_number)
        if len(self.blocks) > self.size.blocks_len:
            self.blocks.pop(0)
            self.block_numbers.pop(0)
            self.block_range = BlockRange(self.block_numbers[0], self.block_numbers[-1])

    def stats(self) -> str:
        return (
            f"blocks = {len(self.blocks)}/{self.size.blocks_len}, "
            f"block_range = {self.block_range.start}->{self.block_range.end}"
        )


class TestData(t.Generic[B]):
    DEFAULT_SIZE = Sizes.S

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

        self._data: BlockchainData | None = None
        self._client: HttpClient | None = None

        self._lock = GeventSemaphore()
        self._logger.debug("Locking")
        self._lock.acquire()
        self._logger.debug("Locked")

    def init_http_client(self, host_url: str) -> None:
        self._client = HttpClient(host_url, timeout=60)
        self._logger.debug("Host: %s", host_url)

    @property
    def initialized(self) -> bool:
        return self._data is not None

    @property
    def data(self) -> BlockchainData:
        if self._data is None:
            raise RuntimeError("Data is not initialized")
        return self._data

    @property
    def client(self) -> HttpClient:
        if self._client is None:
            raise RuntimeError("HTTP Client is not initialized")
        return self._client

    def release_lock(self) -> None:
        self._logger.debug("Releasing lock")
        self._lock.release()
        self._logger.debug("Lock released")

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    def wait(self) -> None:
        self._lock.wait()

    def fetch_block(self, block_number: BlockNumber) -> B:
        raise NotImplementedError

    @retry(reraise=True, stop=stop_after_attempt(5))
    def fetch_latest_block(self) -> B:
        raise NotImplementedError

    @retry(reraise=True, stop=stop_after_attempt(5))
    def fetch_random_block(self, block_numbers: list[BlockNumber]) -> B:
        rng = get_rng()
        while True:
            block_number = self.data.block_range.get_random_block_number(rng)
            if block_number not in block_numbers:
                break
        return self.fetch_block(block_number)

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> BlockRange:
        raise NotImplementedError

    def get_block_from_data(self, data: dict[str, t.Any] | str) -> B:
        raise NotImplementedError

    def init_data(self, parsed_options: Namespace) -> None:
        size: Size = Sizes.get_size(parsed_options.size) if parsed_options.size != "None" else self.DEFAULT_SIZE
        print(f"Test data size: {size.label}")
        self._logger.info(f"Test data size: {size.label}")
        self._data = BlockchainData(size)
        self.data.block_range = self._get_start_and_end_blocks(parsed_options)

    def init_data_from_json(self, json_data: str) -> None:
        data: dict[str, t.Any] = json.loads(json_data)
        size = Size(**data["size"])
        self._data = BlockchainData(size)
        self.data.block_range = BlockRange(**data["block_range"])

    @staticmethod
    def get_random_bool(rng: RNG | None = None) -> bool:
        if rng is None:
            rng = get_rng()
        return rng.random.choice([True, False])

    def get_random_block(self, rng: RNG) -> B:
        return rng.random.choice(self.data.blocks)

    def get_random_block_number(self, rng: RNG | None = None) -> BlockNumber:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).block_number

    @property
    def start_block_number(self) -> BlockNumber:
        return self.data.block_range.start

    @property
    def end_block_number(self) -> BlockNumber:
        return self.data.block_range.end


class SmartContract:
    def __init__(self, address: str):
        self.address = address


class NetworkData(t.TypedDict):
    name: str
    start_block: BlockNumber
    contract_addresses: list[str]
