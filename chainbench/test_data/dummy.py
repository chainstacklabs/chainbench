from chainbench.test_data.base import BaseTestData, BlockchainData


class DummyTestData(BaseTestData):
    def _get_init_data(self):
        return BlockchainData()
