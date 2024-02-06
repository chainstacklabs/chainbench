import logging
import typing as t

from chainbench.test_data.ethereum import EthConsensusTestData

from .http import HttpUser

logger = logging.getLogger(__name__)


class EthConsensusUser(HttpUser):
    abstract = True
    test_data = EthConsensusTestData()

    def eth_beacon_blocks_request(
        self,
        name: str = "eth_beacon_blocks",
        version: str = "v1",
        block_id: int | str = "head",
        path: str | None = None,
    ):
        url_path = f"/eth/{version}/beacon/blocks/{block_id}"
        if path:
            url_path += "/" + path.strip("/")
        self.get(
            name=name,
            path=url_path,
        )

    def eth_v1_beacon_states_validators_request(
        self,
        name: str = "eth_v1_beacon_states_validators",
        state_id: int | str = "head",
        validator_status: str | None = None,
        validator_ids: list[str] | None = None,
    ):
        params: dict[str, t.Any] = {}
        if validator_status:
            params = {"status": validator_status}
        if validator_ids:
            params = {"id": validator_ids}

        self.get(
            name=name,
            path=f"/eth/v1/beacon/states/{state_id}/validators",
            params=params,
        )

    def eth_v1_beacon_headers_request(self, name: str = "eth_v1_beacon_headers", block_id: int | str = "head"):
        self.get(
            name=name,
            path=f"/eth/v1/beacon/headers/{block_id}",
        )


class EthConsensusMethods(EthConsensusUser):
    abstract = True

    def eth_v1_beacon_genesis_task(self):
        self.get(
            name="eth_v1_beacon_genesis",
            path="/eth/v1/beacon/genesis",
        )

    def eth_v1_config_spec_task(self):
        self.get(
            name="eth_v1_config_spec",
            path="/eth/v1/config/spec",
        )

    def eth_v2_beacon_blocks_head_task(self):
        self.eth_beacon_blocks_request(name="eth_v2_beacon_blocks_head", version="v2")

    def eth_v2_beacon_blocks_finalized_task(self):
        self.eth_beacon_blocks_request(name="eth_v2_beacon_blocks_finalized", version="v2", block_id="finalized")

    def eth_v2_beacon_blocks_random_block_id_task(self):
        self.eth_beacon_blocks_request(
            name="eth_v2_beacon_blocks_random_block_id",
            version="v2",
            block_id=self.test_data.get_random_block_number(self.rng.get_rng()),
        )

    def eth_v1_beacon_blocks_random_block_id_root_task(self):
        self.eth_beacon_blocks_request(
            name="eth_v1_beacon_blocks_random_block_id_root",
            block_id=self.test_data.get_random_block_number(self.rng.get_rng()),
            path="root",
        )

    def eth_v1_beacon_blocks_random_block_id_attestations_task(self):
        self.eth_beacon_blocks_request(
            name="eth_v1_beacon_blocks_random_block_id_attestations",
            block_id=self.test_data.get_random_block_number(self.rng.get_rng()),
            path="attestations",
        )

    def eth_v1_beacon_states_validators_head_task(self):
        self.eth_v1_beacon_states_validators_request(
            name="eth_v1_beacon_states_validators_head",
        )

    def eth_v1_beacon_states_validators_random_state_id_task(self):
        self.eth_v1_beacon_states_validators_request(
            name="eth_v1_beacon_states_validators_random_state_id",
            state_id=self.test_data.get_random_block(self.rng.get_rng()).block_number,
        )

    def eth_v1_beacon_states_validators_random_status_task(self):
        self.eth_v1_beacon_states_validators_request(
            name="eth_v1_beacon_states_validators_random_status",
            state_id=self.test_data.get_random_block(self.rng.get_rng()).block_number,
            validator_status=self.test_data.get_random_validator_status(self.rng.get_rng()),
        )

    def eth_v1_beacon_states_validators_random_ids_task(self):
        block = self.test_data.get_random_block(self.rng.get_rng())
        validator_count = self.rng.get_rng().random.randint(50, 100)
        self.eth_v1_beacon_states_validators_request(
            name="eth_v1_beacon_states_validators_random_ids",
            state_id=block.block_number,
            validator_ids=block.get_random_validator_indexes(validator_count, self.rng.get_rng()),
        )

    def eth_v1_beacon_states_validators_random_validator_status_task(self):
        self.eth_v1_beacon_states_validators_request(
            name="eth_v1_beacon_states_validators_random_validator_status",
            state_id=self.test_data.get_random_block(self.rng.get_rng()).block_number,
            validator_status=self.test_data.get_random_validator_status(self.rng.get_rng()),
        )

    def eth_v1_beacon_states_random_state_id_finality_checkpoints_task(self):
        self.get(
            name="eth_v1_beacon_states_finality_checkpoints",
            path=f"/eth/v1/beacon/states/"
            f"{self.test_data.get_random_block(self.rng.get_rng()).block_number}/finality_checkpoints",
        )

    def eth_v1_validator_duties_proposer_random_epoch_task(self):
        self.get(
            name="eth_v1_validator_duties_proposer_random_epoch",
            path=f"/eth/v1/validator/duties/proposer/{self.test_data.get_random_epoch(self.rng.get_rng())}",
        )

    def eth_v1_beacon_states_head_committees_task(self):
        self.get(
            name="eth_v1_beacon_states_committees",
            path="/eth/v1/beacon/states/head/committees",
        )

    def eth_v1_beacon_states_head_committees_random_epoch_task(self):
        self.get(
            name="eth_v1_beacon_states_committees_random_epoch",
            path=f"/eth/v1/beacon/states/head/committees?"
            f"epoch={self.test_data.get_random_epoch(self.rng.get_rng())}",
        )

    def eth_v1_beacon_headers_head_task(self):
        self.eth_v1_beacon_headers_request(
            name="eth_v1_beacon_headers_head",
        )

    def eth_v1_beacon_headers_random_block_id_task(self):
        self.eth_v1_beacon_headers_request(
            name="eth_v1_beacon_headers_random_block_id",
            block_id=self.test_data.get_random_block_number(self.rng.get_rng()),
        )

    def eth_v1_node_health_task(self):
        self.get(
            name="eth_v1_node_health",
            path="/eth/v1/node/health",
        )

    def eth_v1_node_version_task(self):
        self.get(
            name="eth_v1_node_version",
            path="/eth/v1/node/version",
        )
