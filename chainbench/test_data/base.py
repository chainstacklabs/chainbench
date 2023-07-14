import logging
import typing as t
from dataclasses import dataclass, field
from secrets import token_hex

import httpx
from gevent.lock import Semaphore as GeventSemaphore

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


@dataclass
class BlockchainData:
    start_block_number: BlockNumber = 0
    end_block_number: BlockNumber = 0
    blocks: Blocks = field(default_factory=list)
    txs: Txs = field(default_factory=list)
    tx_hashes: TxHashes = field(default_factory=list)
    accounts: Accounts = field(default_factory=list)


class BaseTestData:
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

    def update(self, host_url: str):
        self._logger.info("Updating data")
        self._host = host_url
        self._logger.debug("Host: %s", self._host)
        data = self._get_init_data()
        self._logger.info("Data fetched")
        self._logger.debug("Data: %s", data)
        self._data = data
        self._logger.info("Data updated. Releasing lock")
        self._lock.release()
        self._logger.info("Lock released")
        return data

    def _get_init_data(self) -> BlockchainData:
        raise NotImplementedError

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

    def _make_body(self, method: str, params: list[t.Any] | None = None):
        if params is None:
            params = []

        return {
            "jsonrpc": self._rpc_version,
            "method": method,
            "params": params,
            "id": token_hex(8),
        }

    def _make_call(self, method: str, params: list[t.Any] | None = None):
        if params is None:
            params = []

        response = self._client.post(
            self.host,
            json=self._make_body(method, params),
        )

        self._logger.debug(
            f"Making call to {self.host} with method {method} and params {params}"
        )
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

    def close(self):
        self._client.close()

    def wait(self):
        self._lock.wait()

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

    def get_random_recent_block_number(
        self, n: int, rng: RNG | None = None
    ) -> BlockNumber:
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
