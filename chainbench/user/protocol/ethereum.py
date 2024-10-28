import logging
import typing as t

from locust import tag, task

from chainbench.test_data.ethereum import EthBeaconTestData
from chainbench.user.http import HttpUser
from chainbench.user.wss import WSSubscription
from chainbench.util.rng import RNGManager

logger = logging.getLogger(__name__)


class EthBeaconBaseUser(HttpUser):
    abstract = True
    test_data = EthBeaconTestData()
    rng = RNGManager()

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

    def eth_v1_beacon_states_sync_committees_request(
        self,
        name: str = "eth_v1_beacon_states_sync_committees",
        state_id: int | str = "head",
        epoch: int | None = None,
    ):
        params: dict[str, t.Any] = {}
        if epoch:
            params = {"epoch": epoch}
        self.get(
            name=name,
            path=f"/eth/v1/beacon/states/{state_id}/sync_committees",
            params=params,
        )

    def eth_v1_beacon_headers_request(
        self,
        name: str = "eth_v1_beacon_headers",
        block_id: int | str | None = None,
        slot: int | None = None,
        parent_root: str | None = None,
    ):
        path = ""
        if block_id is not None:
            path = f"/{block_id}"
        params: dict[str, t.Any] = {}
        if slot is not None:
            params["slot"] = slot
        if parent_root is not None:
            params["parent_root"] = parent_root
        self.get(name=name, path="/eth/v1/beacon/headers" + path, params=params)

    def eth_v1_beacon_states_committees_request(
        self,
        name: str = "eth_v1_beacon_states_committees",
        state_id: int | str = "head",
        epoch: int | None = None,
        committee_index: int | None = None,
        slot: int | None = None,
    ):
        params: dict[str, t.Any] = {}
        if epoch is not None:
            params["epoch"] = epoch
        if committee_index is not None:
            params["committee_index"] = committee_index
        if slot is not None:
            params["slot"] = slot
        self.get(name=name, path=f"/eth/v1/beacon/states/{state_id}/committees", params=params)


class EthBeaconUser(EthBeaconBaseUser):
    abstract = True

    @staticmethod
    def task_to_method(task_name: str) -> str:
        task_name_stripped = task_name.replace("_task", "")
        return f"{task_name_stripped}"

    @classmethod
    def method_to_task_function(cls, method: str) -> t.Callable:
        if not method.endswith("task"):
            return getattr(cls, f"{method}_task")
        else:
            return getattr(cls, method)

    def eth_v1_beacon_states_head_fork_task(self):
        self.get(
            name="eth_v1_beacon_states_head_fork",
            path="/eth/v1/beacon/states/head/fork",
        )

    def eth_v1_beacon_states_random_state_id_fork_task(self):
        self.get(
            name="eth_v1_beacon_states_random_state_id_fork",
            path=f"/eth/v1/beacon/states/{self.test_data.get_random_block_number(self.rng.get_rng())}/fork",
        )

    def eth_v1_beacon_genesis_task(self):
        self.get(
            name="eth_v1_beacon_genesis",
            path="/eth/v1/beacon/genesis",
        )

    def eth_v1_config_fork_schedule_task(self):
        self.get(
            name="eth_v1_config_fork_schedule",
            path="/eth/v1/config/fork_schedule",
        )

    def eth_v1_config_spec_task(self):
        self.get(
            name="eth_v1_config_spec",
            path="/eth/v1/config/spec",
        )

    def eth_v1_config_deposit_contract_task(self):
        self.get(
            name="eth_v1_config_deposit_contract",
            path="/eth/v1/config/deposit_contract",
        )

    def eth_v1_beacon_pool_voluntary_exits_task(self):
        self.get(
            name="eth_v1_beacon_pool_voluntary_exits",
            path="/eth/v1/beacon/pool/voluntary_exits",
        )

    def eth_v1_beacon_pool_proposer_slashings_task(self):
        self.get(
            name="eth_v1_beacon_pool_proposer_slashings",
            path="/eth/v1/beacon/pool/proposer_slashings",
        )

    def eth_v1_beacon_pool_attester_slashings_task(self):
        self.get(
            name="eth_v1_beacon_pool_attester_slashings",
            path="/eth/v1/beacon/pool/attester_slashings",
        )

    def eth_v1_beacon_pool_attestations_task(self):
        self.get(
            name="eth_v1_beacon_pool_attestations",
            path="/eth/v1/beacon/pool/attestations",
        )

    def eth_v1_beacon_states_head_validator_balances_task(self):
        self.get(
            name="eth_v1_beacon_states_head_validator_balances",
            path="/eth/v1/beacon/states/head/validator_balances",
        )

    def eth_v1_beacon_states_random_state_id_validator_balances_task(self):
        self.get(
            name="eth_v1_beacon_states_random_state_id_validator_balances",
            path=f"/eth/v1/beacon/states/{self.test_data.get_random_block_number(self.rng.get_rng())}"
            f"/validator_balances",
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

    def eth_v1_beacon_states_random_state_id_finality_checkpoints_task(self):
        self.get(
            name="eth_v1_beacon_random_states_finality_checkpoints",
            path=f"/eth/v1/beacon/states/"
            f"{self.test_data.get_random_block(self.rng.get_rng()).block_number}/finality_checkpoints",
        )

    def eth_v1_validator_duties_proposer_random_epoch_task(self):
        self.get(
            name="eth_v1_validator_duties_proposer_random_epoch",
            path=f"/eth/v1/validator/duties/proposer/{self.test_data.get_random_epoch(self.rng.get_rng())}",
        )

    def eth_v1_beacon_states_head_committees_task(self):
        self.eth_v1_beacon_states_committees_request(name="eth_v1_beacon_states_head_committees")

    def eth_v1_beacon_states_head_committees_random_epoch_task(self):
        self.eth_v1_beacon_states_committees_request(
            name="eth_v1_beacon_states_head_committees_random_epoch",
            epoch=self.test_data.get_random_epoch(self.rng.get_rng()),
        )

    def eth_v1_beacon_states_random_state_id_committees_task(self):
        self.eth_v1_beacon_states_committees_request(
            name="eth_v1_beacon_states_random_state_id_committees",
            state_id=self.test_data.get_random_block(self.rng.get_rng()).block_number,
        )

    def eth_v1_beacon_states_random_state_id_root_task(self):
        self.get(
            name="eth_v1_beacon_states_random_state_id_root",
            path=f"/eth/v1/beacon/states/{self.test_data.get_random_block(self.rng.get_rng()).block_number}/root",
        )

    def eth_v1_beacon_states_head_root_task(self):
        self.get(
            name="eth_v1_beacon_states_head_root",
            path="/eth/v1/beacon/states/head/root",
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

    def eth_v1_beacon_headers_random_slot_task(self):
        self.eth_v1_beacon_headers_request(
            name="eth_v1_beacon_headers_random_slot",
            slot=self.test_data.get_random_block_number(self.rng.get_rng()),
        )

    def eth_v1_beacon_states_random_state_id_sync_committees_task(self):
        self.eth_v1_beacon_states_sync_committees_request(
            name="eth_v1_beacon_states_random_state_id_sync_committees",
            state_id=self.test_data.get_random_block_number(self.rng.get_rng()),
        )

    def eth_v1_beacon_states_head_sync_committees_task(self):
        self.eth_v1_beacon_states_sync_committees_request(
            name="eth_v1_beacon_states_head_sync_committees",
        )

    def eth_v1_beacon_states_random_state_id_sync_committees_random_epoch_task(self):
        block = self.test_data.get_random_block(self.rng.get_rng())
        self.eth_v1_beacon_states_sync_committees_request(
            name="eth_v1_beacon_states_random_state_id_sync_committees_random_epoch",
            state_id=block.block_number,
            epoch=block.epoch,
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


class TestEthMethod(EthBeaconUser):
    @tag("single")
    @task
    def run_task(self) -> None:
        self.method_to_task_function(self.environment.parsed_options.method)(self)


class EthSubscribe(WSSubscription):
    def __init__(self, params: dict | list):
        super().__init__("eth_subscribe", params, "eth_unsubscribe")
