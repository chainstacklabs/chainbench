import json
import logging
import typing as t
from argparse import Namespace
from dataclasses import dataclass
from json import JSONDecodeError
from secrets import token_hex

import httpx
from gevent.lock import Semaphore as GeventSemaphore
from tenacity import retry, stop_after_attempt

from chainbench.util.rng import RNG, get_rng

logger = logging.getLogger(__name__)

Account = str
TxHash = str
Tx = dict[str, t.Any]
BlockNumber = int
BlockHash = str


class HelperMixin:
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


class RPCError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"RPC Error: {code} - {message}")


class HttpxClient:
    def __init__(self, host: str, rpc_version: str = "2.0"):
        self._rpc_version = rpc_version
        self._host = host
        self._client = httpx.Client()

    def close(self) -> None:
        self._client.close()

    def _make_body(self, method: str, params: list[t.Any] | None = None) -> dict[str, t.Any]:
        if params is None:
            params = []

        return {
            "jsonrpc": self._rpc_version,
            "method": method,
            "params": params,
            "id": token_hex(8),
        }

    def make_call(self, method: str, params: list[t.Any] | None = None) -> t.Any:
        if params is None:
            params = []

        response = self._client.post(
            self._host,
            json=self._make_body(method, params),
        )

        logger.debug(f"Making call to {self._host} with method {method} and params {params}")
        logger.debug(f"Response: {response.text}")

        response.raise_for_status()

        # check if response is json
        try:
            data: dict[str, t.Any] = response.json()
        except JSONDecodeError:
            logger.error("Response is not json: %s", response.text)
            raise

        # check if response is error
        if "error" in data:
            logger.error("Response is error: %s", response.text)
            raise RPCError(code=data["error"]["code"], message=data["error"]["message"])

        # check if response is valid
        if "result" not in data:
            logger.error("Response is not valid: %s", response.text)
            raise ValueError(response.text)

        return data["result"]


@dataclass
class Block(HelperMixin):
    block_number: BlockNumber

    def to_json(self) -> str:
        return json.dumps(self.__dict__)


@dataclass
class BlockRange:
    start: BlockNumber
    end: BlockNumber


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
        self.block_range: BlockRange = BlockRange(start, end)
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


class TestData(HelperMixin, t.Generic[B]):
    DEFAULT_SIZE: Size = Sizes.S

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

        self._parsed_options: Namespace | None = None
        self._data: BlockchainData | None = None
        self._client: HttpxClient | None = None

        self._lock = GeventSemaphore()
        self._logger.debug("Locking")
        self._lock.acquire()
        self._logger.debug("Locked")

    def init_http_client(self, host_url: str):
        self._client = HttpxClient(host_url)
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
    def client(self) -> HttpxClient:
        if self._client is None:
            raise RuntimeError("HTTP Client is not initialized")
        return self._client

    @property
    def parsed_options(self) -> Namespace:
        if self._parsed_options is None:
            raise RuntimeError("Parsed Options is not initialized")
        return self._parsed_options

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    def wait(self) -> None:
        self._lock.wait()

    def fetch_block(self, block_number: BlockNumber) -> B:
        raise NotImplementedError

    @retry(reraise=True, stop=stop_after_attempt(5))
    def _fetch_random_block(self, block_numbers: list[BlockNumber]) -> B:
        rng: RNG = get_rng()
        while True:
            block_number: BlockNumber = rng.random.randint(self.data.block_range.start, self.data.block_range.end)
            if block_number not in block_numbers:
                break
        return self.fetch_block(block_number)

    def _get_start_and_end_blocks(self, use_latest_blocks: bool) -> BlockRange:
        raise NotImplementedError

    def _get_data_from_blockchain(self, input_size: str, use_latest_blocks: bool) -> None:
        size: Size = Sizes.get_size(input_size) if input_size != "None" else self.DEFAULT_SIZE
        print(f"Test data size: {size.label}")
        self._logger.info(f"Test data size: {size.label}")
        self._data = BlockchainData(size)
        self.data.block_range = self._get_start_and_end_blocks(use_latest_blocks)

        if use_latest_blocks:
            print(f"Using latest {size.blocks_len} blocks as test data")
            self._logger.info(f"Using latest {size.blocks_len} blocks as test data")
            for block_number in range(self.data.block_range.start, self.data.block_range.end + 1):
                self.data.push_block(self.fetch_block(block_number))
                print(self.data.stats(), end="\r")
            else:
                print(self.data.stats(), end="\r")
                print("\n")  # new line after progress display upon exiting loop
        else:
            while size.blocks_len > len(self.data.blocks):
                block: B = self._fetch_random_block(self.data.block_numbers)
                self.data.push_block(block)
                print(self.data.stats(), end="\r")
            else:
                print(self.data.stats(), end="\r")
                print("\n")  # new line after progress display upon exiting loop

    def get_block_from_data(self, data: dict[str, t.Any] | str) -> B:
        raise NotImplementedError

    def _get_data_from_json(self, json_data: str) -> None:
        data: dict[str, t.Any] = json.loads(json_data)
        size = Size(**data["size"])
        self._data = BlockchainData(size)
        self.data.block_range = BlockRange(**data["block_range"])
        self.data.blocks = [self.get_block_from_data(block) for block in data["blocks"]]
        self.data.block_numbers = data["block_numbers"]

    def _update_data(self, init_function: t.Callable, *args, **kwargs) -> None:
        self._logger.info("Updating data")
        init_function(*args, **kwargs)
        self._logger.debug("Data: %s", self.data.to_json())
        self._logger.info("Data updated. Releasing lock")
        self._lock.release()
        self._logger.info("Lock released")

    def set_parsed_options(self, parsed_options: Namespace) -> None:
        self._parsed_options = parsed_options

    def init_data_from_blockchain(self) -> None:
        self._update_data(
            self._get_data_from_blockchain, self.parsed_options.size, self.parsed_options.use_latest_blocks
        )

    def init_data_from_json(self, json_data: str) -> None:
        self._update_data(self._get_data_from_json, json_data)

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
