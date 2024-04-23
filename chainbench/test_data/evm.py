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
    InvalidBlockError,
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
        11155111: {
            "name": "ethereum-sepolia-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x7451ee8EeCf3b8534FA07B15b4B5ceE4bCc88778",
                "0x3593B75e2a849DFDACb7e1ADdA24cB836670532b",
                "0xFd57b4ddBf88a4e07fF4e34C487b99af2Fe82a05",
                "0x397a59aA02eB65702E5DAdDd5967bbe1979F9aC3",
                "0x466D489b6d36E7E3b824ef491C225F5830E81cC1",
                "0x26fb2eee2F48d6EB3111e5aF0b3F11E6694296a8",
                "0xc132ec2e4B6130273AE6C6eD0a1B8bEE2C3815a0",
                "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
                "0x4c16D8C078eF6B56700C1BE19a336915962df072",
                "0x097D90c9d3E0B50Ca60e1ae45F6A81010f9FB534",
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
        97: {
            "name": "bsc-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0xbDa40aCd71540DE69e3D85f88f9fd0E97f575A7F",
                "0x337610d27c682E347C9cD60BD4b3b107C9d34dDd",
                "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",
                "0x1efde6C6346EEdD82576903F65c7eC4141C54FFf",
                "0x0000000000000000000000000000000000002005",
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
        80002: {
            "name": "polygon-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582",
                "0xF9bAfe82B6B65091580E403BC0B6F8d15b59FaF6",
                "0xC4Af1A414d115882CE5E270C2a42888AeF5d75D5",
                "0x13F793FAadA9b42BeFEF18048658813CF6FE790F",
                "0x48bD4aD223b2d454c045aBF22CDa1b716B64d380",
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
        43113: {
            "name": "avalanche-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x5425890298aed601595a70AB815c96711a31Bc65",
                "0xA089a21902914C3f3325dBE2334E9B466071E5f1",
                "0xd00B9BBC6EDC3953Ec502d73E7FA7C59f628d947",
                "0x45ea5d57BA80B5e3b0Ed502e9a08d568c96278F9",
                "0xEdDEB2ff49830f3aa30Fee2F7FaBC5136845304a",
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
        84532: {
            "name": "base-sepolia-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x87C51CD469A0E1E2aF0e0e597fD88D9Ae4BaA967",
                "0xBF916435e1E3548525F4e3Fe851c5aB0Da3F8Bf1",
                "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                "0xf960d27DC82e5a587441CCbFa8B0Ba7E0f8740B3",
                "0x3a673d6896Ee19dd3d7930563792848B1BEd84dF",
            ],
        },
        42161: {
            "name": "arbitrum-mainnet",
            "start_block": 1,
            "contract_addresses": [
                "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
                "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
                "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
                "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
                "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
                "0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0",
                "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
                "0x912CE59144191C1204E64559FE8253a0e49E6548",
                "0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
                "0x9623063377AD1B27544C965cCd7342f7EA7e88C7",
            ],
        },
        421614: {
            "name": "arbitrum-sepolia-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x9aA40Cc99973d8407a2AE7B2237d26E615EcaFd2",
                "0x3E27fAe625f25291bFda517f74bf41DC40721dA2",
                "0x980B62Da83eFf3D4576C647993b0c1D7faf17c73",
                "0xDbc8c016287437ce2cF69fF64c245A4D74599A40",
                "0xb1D4538B4571d411F07960EF2838Ce337FE1E80E",
            ],
        },
        10: {
            "name": "optimism-mainnet",
            "start_block": 1,
            "contract_addresses": [
                "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
                "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
                "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
                "0x68f180fcCe6836688e9084f035309E29Bf0A2095",
                "0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6",
                "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
                "0x4200000000000000000000000000000000000042",
                "0xFdb794692724153d1488CcdBE0C56c252596735F",
                "0xdC6fF44d5d932Cbd77B52E5612Ba0529DC6226F1",
                "0x99C59ACeBFEF3BBFB7129DC90D1a11DB0E91187f",
            ],
        },
        11155420: {
            "name": "optimism-sepolia-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x5fd84259d66Cd46123540766Be93DFE6D43130D7",
                "0xb210fba65DC617bE30eB6B0b99B3CDd5556EF82e",
                "0x298b4c4F9bE251c100724a3bEAe234BD1652CBcE",
                "0xE4aB69C077896252FAFBD49EFD26B5D171A32410",
                "0x0c21E17F8F9131260FA264dD56C8395F7B692149",
            ],
        },
        250: {
            "name": "fantom-mainnet",
            "start_block": 1,
            "contract_addresses": [
                "0xBE41772587872A92184873d55B09C6bB6F59f895",
                "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75",
                "0x82f0B8B456c1A451378467398982d4834b6829c1",
                "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",
                "0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590",
                "0x841FAD6EAe12c286d1Fd18d1d525DFfA75C7EFFE",
                "0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E",
                "0x5Cc61A78F164885776AA610fb0FE1257df78E59B",
                "0x049d68029688eAbF473097a2fC38ef61633A3C7A",
                "0x6c021Ae822BEa943b2E66552bDe1D2696a53fbB7",
            ],
        },
        4002: {
            "name": "fantom-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0xeccCAf43A81AADf68962346c62F07f8e9bfDa3AA",
                "0xf1277d1Ed8AD466beddF92ef448A132661956621",
                "0x75Cc4fDf1ee3E781C1A3Ee9151D5c6Ce34Cf5C61",
                "0xEAe1274dBdD006b5eA3197729BF5f11B8fbb427E",
                "0x5538e600dc919f72858dd4D4F5E4327ec6f2af60",
            ],
        },
        2020: {
            "name": "ronin-mainnet",
            "start_block": 1,
            "contract_addresses": [
                "0xa8754b9fa15fc18bb59458815510e40a12cd2014",
                "0xc99a6a985ed2cac1ef41640596c5a5f9f4e19ef5",
                "0x97a9107c1793bc407d6f527b77e7fff4d812bece",
                "0xc39a2430b0b6f1edad1681672b47c857c1be0998",
                "0xe514d9deb7966c8be0ca922de8a064264ea6bcd4",
                "0x0b7007c13325c48911f73a2dad5fa5dcbf808adc",
                "0x7eae20d11ef8c779433eb24503def900b9d28ad7",
                "0x1b918543b518e34902e1e8dd76052bee43c762ff",
                "0x306a28279d04a47468ed83d55088d0dcd1369294",
                "0x2ecb08f87f075b5769fe543d0e52e40140575ea7",
            ],
        },
        2021: {
            "name": "ronin-testnet",
            "start_block": 1,
            "contract_addresses": [
                "0x3c4e17b9056272ce1b49f6900d8cfd6171a1869d",
                "0x29c6f8349a028e1bdfc68bfa08bdee7bc5d47e16",
                "0xa959726154953bae111746e265e6d754f48570e6",
                "0x04ef1d4f687bb20eedcf05c7f710c078ba39f328",
                "0x067fbff8990c58ab90bae3c97241c5d736053f77",
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
        block = EvmBlock.from_response(parse_hex_to_int(result["number"]), result)
        if len(block.txs) == 0:
            raise InvalidBlockError
        return block

    def fetch_latest_block(self) -> EvmBlock:
        return self.fetch_block("latest")

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
