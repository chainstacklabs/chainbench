import random

from chainbench.test_data.base import BaseTestData, BlockchainData


class EVMTestData(BaseTestData):
    TXS_REQUIRED = 50
    SAVE_LAST_BLOCKS = 100

    @staticmethod
    def _parse_hex_to_int(value: str) -> int:
        return int(value, 16)

    def _fetch_block(
        self, block_number: int | str, return_txs: bool = True
    ) -> tuple[int, dict]:
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
        block_number = random.randint(start, end)
        return self._fetch_block(block_number, return_txs=return_txs)

    # get initial data from blockchain
    def _get_init_data(self) -> BlockchainData:
        latest_block_number, latest_block = self._fetch_block("latest")
        txs = []
        tx_hashes = []
        accounts = []
        blocks = [(latest_block_number, latest_block["hash"])]
        # extract data from block
        for tx in latest_block["transactions"]:
            txs.append(tx)
            tx_hashes.append(tx["hash"])
            accounts.append(tx["from"])
            accounts.append(tx["to"])

        while self.TXS_REQUIRED > len(txs):
            block_number, block = self._fetch_random_block(0, latest_block_number)
            blocks.append((block_number, block["hash"]))
            for tx in block["transactions"]:
                txs.append(tx)
                tx_hashes.append(tx["hash"])
                accounts.append(tx["from"])
                accounts.append(tx["to"])

        return BlockchainData(
            latest_block_number=latest_block_number,
            latest_block=latest_block,
            first_block_number=0,
            blocks=blocks,
            txs=txs,
            tx_hashes=tx_hashes,
            accounts=accounts,
        )

    def get_random_recent_block_number_hex(self, n: int | None = None) -> str:
        if n is None:
            n = self.SAVE_LAST_BLOCKS
        return hex(
            random.randint(
                self.latest_block_number - n,
                self.latest_block_number,
            )
        )

    def get_random_block_number_hex(self) -> str:
        return hex(self.get_random_block_number())
