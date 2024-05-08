"""
Ethereum Beacon profile.
"""

from locust import constant_pacing

from chainbench.user.tasks.ethereum import EthBeaconMethods

# mypy: ignore_errors


class EthereumBeaconProfile(EthBeaconMethods):
    wait_time = constant_pacing(1)
    tasks = {
        EthBeaconMethods.eth_v1_beacon_states_validators_random_ids_task: 698,
        EthBeaconMethods.eth_v1_beacon_states_validators_head_task: 23,
        EthBeaconMethods.eth_v1_beacon_states_head_committees_random_epoch_task: 10,
        EthBeaconMethods.eth_v1_beacon_states_validators_random_status_task: 10,
        EthBeaconMethods.eth_v1_beacon_states_random_state_id_finality_checkpoints_task: 10,
        EthBeaconMethods.eth_v2_beacon_blocks_random_block_id_task: 8,
        EthBeaconMethods.eth_v2_beacon_blocks_head_task: 6,
        EthBeaconMethods.eth_v1_beacon_headers_head_task: 4,
        EthBeaconMethods.eth_v1_config_spec_task: 3,
        EthBeaconMethods.eth_v1_node_health_task: 2,
        EthBeaconMethods.eth_v2_beacon_blocks_finalized_task: 1,
        EthBeaconMethods.eth_v1_beacon_headers_random_block_id_task: 1,
        EthBeaconMethods.eth_v1_node_version_task: 1,
    }
