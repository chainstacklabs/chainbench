from configargparse import Namespace

from chainbench.test_data.base import BaseTestData, BlockchainData


class DummyTestData(BaseTestData):
    def _get_init_data_from_blockchain(self, parsed_options: Namespace) -> BlockchainData:
        return BlockchainData()
