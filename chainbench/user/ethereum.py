import logging
import typing as t

from chainbench.test_data.ethereum import EthBeaconTestData

from .http import HttpUser

logger = logging.getLogger(__name__)


class EthBeaconUser(HttpUser):
    abstract = True
    test_data = EthBeaconTestData()

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
