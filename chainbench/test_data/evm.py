import json
import logging
import typing as t
from argparse import Namespace
from dataclasses import dataclass

from chainbench.util.rng import RNG, get_rng

from .blockchain import (
    Account,
    Block,
    BlockHash,
    BlockNumber,
    BlockRange,
    NetworkData,
    SmartContract,
    TestData,
    Tx,
    TxHash,
    append_if_not_none,
    parse_hex_to_int,
)

logger = logging.getLogger(__name__)

ChainId = int


class Erc20Contract(SmartContract):
    def total_supply_params(self) -> dict[str, str]:
        return {"data": "0x18160ddd", "to": self.address}

    def balance_of_params(self, target_address: str) -> dict[str, str]:
        return {"data": "0x70a08231" + target_address[2:].zfill(64), "to": self.address}

    def symbol_params(self) -> dict[str, str]:
        return {"data": "0x95d89b41", "to": self.address}

    def name_params(self) -> dict[str, str]:
        return {"data": "0x06fdde03", "to": self.address}


class EvmNetwork:
    def __new__(cls, chain_id: ChainId):
        if chain_id not in cls.DATA:
            raise ValueError(f"Unsupported chain id: {chain_id}")
        return super().__new__(cls)

    def __init__(self, chain_id: ChainId):
        self.chain_id = chain_id

    @property
    def name(self) -> str:
        return self.DATA[self.chain_id]["name"]

    @property
    def start_block(self) -> BlockNumber:
        return self.DATA[self.chain_id]["start_block"]

    @property
    def contract_addresses(self) -> list[str]:
        try:
            result: list[str] = self.DATA[self.chain_id]["contract_addresses"]
            if len(result) == 0:
                raise ValueError
        except (ValueError, KeyError):
            raise ValueError(f"Chain {self.name} does not have contract addresses")
        else:
            return result

    def get_contracts(self) -> list[Erc20Contract]:
        return [Erc20Contract(address) for address in self.contract_addresses]

    def get_random_contract(self, rng: RNG) -> Erc20Contract:
        return rng.random.choice(self.get_contracts())

    DATA: t.Mapping[ChainId, NetworkData] = {
        1: {
            "name": "ethereum-mainnet",
            "start_block": 10000000,
            "contract_addresses": [
                "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "0xB8c77482e45F1F44dE1745F52C74426C631bDD52",
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
                "0x514910771AF9Ca656af840dff83E8264EcF986CA",
                "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
                "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
                "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            ],
        },
        56: {
            "name": "bsc-mainnet",
            "start_block": 20000000,
            "contract_addresses": [
                "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                "0x55d398326f99059fF775485246999027B3197955",
                "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
                "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47",
                "0x1CE0c2827e2eF14D5C4f29a091d735A204794041",
                "0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                "0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402",
                "0xF8A0BF9cF54Bb92F17374d9e9A321E6a111a51bD",
            ],
        },
        137: {
            "name": "polygon-mainnet",
            "start_block": 35000000,
            "contract_addresses": [
                "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
                "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
                "0x2C89bbc92BD86F8075d1DEcc58C7F4E0107f286b",
                "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
                "0x0000000000000000000000000000000000001010",
                "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
                "0x6f8a06447Ff6FcF75d803135a7de15CE88C1d4ec",
                "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
                "0xb33EaAd8d922B1083446DC23f610c2567fB5180f",
            ],
        },
        23294: {
            "name": "oasis-sapphire-mainnet",
            "start_block": 0,
            "contract_addresses": [
                "0x39d22B78A7651A76Ffbde2aaAB5FD92666Aca520",
                "0x8Bc2B030b299964eEfb5e1e0b36991352E56D2D3",
                "0x6b59C68405B0216C2C8ba1EC1f8DCcBd47892c58",
                "0xda4ff51d969aC5982F7eA284c27E8Ed6b8BD1a7c",
                "0xE48151964556381B33f93E05E36381Fd53Ec053E",
                "0xa349005a68FA33e8DACAAa850c45175bbcD49B19",
            ],
        },
        43114: {
            "name": "avalanche-mainnet",
            "start_block": 20000000,
            "contract_addresses": [
                "0x63a72806098Bd3D9520cC43356dD78afe5D386D9",
                "0x5947BB275c521040051D82396192181b413227A3",
                "0xc7198437980c041c805A1EDcbA50c1Ce5db95118",
                "0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB",
                "0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664",
                "0xFE6B19286885a4F7F55AdAD09C3Cd1f906D2478F",
                "0x2147EFFF675e4A4eE1C2f918d181cDBd7a8E208f",
                "0x39cf1BD5f15fb22eC3D9Ff86b0727aFc203427cc",
                "0x19860CCB0A68fd4213aB9D8266F7bBf05A8dDe98",
                "0x8a0cAc13c7da965a312f08ea4229c37869e85cB9",
            ],
        },
        8453: {
            "name": "base-mainnet",
            "start_block": 1,
            "contract_addresses": [
                "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
                "0x4A3A6Dd60A34bB2Aba60D73B4C88315E9CeB6A3D",
                "0x703D57164CA270b0B330A87FD159CfEF1490c0a5",
                "0x09188484e1Ab980DAeF53a9755241D759C5B7d60",
                "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
                "0x4200000000000000000000000000000000000006",
                "0xE3B53AF74a4BF62Ae5511055290838050bf764Df",
                "0x78a087d713Be963Bf307b18F2Ff8122EF9A63ae9",
            ],
        },
        84531: {
            "name": "base-goerli-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x231401dC8b53338d78c08f83CC4EBc74148196d0",
                "0xF175520C52418dfE19C8098071a252da48Cd1C19",
                "0x4B2d9827F7Ee26e8e1732b4614A35fBEa1f06D7A",
                "0x41927EfAd7C649DB0605E53d7D409AEb2F499608",
                "0xf0efcf5b2e7E8580d7D7aac0c11f5066541585D0",
            ],
        },
        # TODO: Move StarkNet out of EVMNetwork
        23448594291968334: {
            "name": "starknet-mainnet",
            "start_block": 100000,
            "contract_addresses": [],
        },
    }


@dataclass(frozen=True)
class EvmBlock(Block):
    block_hash: BlockHash
    txs: list[Tx]
    tx_hashes: list[TxHash]
    accounts: list[Account]

    @classmethod
    def from_response(cls, block_number: BlockNumber, data: dict[str, t.Any]):
        block_hash: BlockHash = data["hash"]
        txs: list[Tx] = data["transactions"]
        tx_hashes: list[TxHash] = []
        accounts: set[Account] = set()
        for index, tx in enumerate(txs):
            if index == 100:
                # limit it to 100 per block
                break
            append_if_not_none(accounts, tx["from"])
            append_if_not_none(accounts, tx["to"])
            append_if_not_none(tx_hashes, tx["hash"])
        return cls(block_number, block_hash, txs, tx_hashes, list(accounts))

    def get_random_tx(self, rng: RNG) -> Tx:
        return rng.random.choice(self.txs)

    def get_random_tx_hash(self, rng: RNG) -> TxHash:
        return rng.random.choice(self.tx_hashes)

    def get_random_account(self, rng: RNG) -> Account:
        return rng.random.choice(self.accounts)


class EvmTestData(TestData[EvmBlock]):
    def __init__(self, network: EvmNetwork | None = None):
        super().__init__()
        self._network = network

    def init_network(self, chain_id: ChainId):
        self._network = EvmNetwork(chain_id)

    @property
    def network(self):
        if self._network is None:
            raise RuntimeError("Network is not set")
        return self._network

    def get_random_erc20_contract(self, rng: RNG) -> Erc20Contract:
        return self.network.get_random_contract(rng)

    def get_block_from_data(self, data: dict[str, t.Any] | str) -> EvmBlock:
        if isinstance(data, str):
            data_dict = json.loads(data)
        else:
            data_dict = data
        return EvmBlock(**data_dict)

    def fetch_chain_id(self) -> ChainId:
        return parse_hex_to_int(self.client.make_rpc_call("eth_chainId"))

    def fetch_latest_block_number(self) -> BlockNumber:
        return parse_hex_to_int(self.client.make_rpc_call("eth_blockNumber"))

    def fetch_block(self, block_number: BlockNumber | str) -> EvmBlock:
        if isinstance(block_number, int):
            block_number = hex(block_number)
        elif (block_number := block_number.lower()) not in [
            "latest",
            "earliest",
            "pending",
        ]:
            raise ValueError("Invalid block number")
        result: dict[str, t.Any] = self.client.make_rpc_call("eth_getBlockByNumber", [block_number, True])
        return EvmBlock.from_response(parse_hex_to_int(result["number"]), result)

    def _get_start_and_end_blocks(self, parsed_options: Namespace) -> BlockRange:
        end_block_number = self.fetch_latest_block_number()
        if parsed_options.use_latest_blocks:
            start_block_number = end_block_number - self.data.size.blocks_len + 1
        else:
            start_block_number = self.network.start_block
            logger.info("Using blocks from %s to %s as test data", start_block_number, end_block_number)
        return BlockRange(start_block_number, end_block_number)

    def get_random_block_hash(self, rng: RNG | None = None) -> BlockHash:
        if rng is None:
            rng = get_rng()
        return self.get_random_block(rng).block_hash

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
