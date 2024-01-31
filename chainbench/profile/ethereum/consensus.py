"""
Ethereum Consensus profile.
"""
from locust import constant_pacing

from chainbench.user.ethereum import EthConsensusMethods

# mypy: ignore_errors


class EthereumConsensusProfile(EthConsensusMethods):
    wait_time = constant_pacing(1)
    tasks = {
        EthConsensusMethods.eth_v1_beacon_states_validators_random_ids_task: 698,
        EthConsensusMethods.eth_v1_beacon_states_validators_head_task: 23,
        EthConsensusMethods.eth_v1_beacon_states_head_committees_random_epoch_task: 10,
        EthConsensusMethods.eth_v1_beacon_states_validators_random_validator_status_task: 10,
        EthConsensusMethods.eth_v1_beacon_states_random_state_id_finality_checkpoints_task: 10,
        EthConsensusMethods.eth_v2_beacon_blocks_random_block_id_task: 8,
        EthConsensusMethods.eth_v2_beacon_blocks_head_task: 6,
        EthConsensusMethods.eth_v1_beacon_headers_head_task: 4,
        EthConsensusMethods.eth_v1_config_spec_task: 3,
        EthConsensusMethods.eth_v1_node_health_task: 2,
        EthConsensusMethods.eth_v2_beacon_blocks_finalized_task: 1,
        EthConsensusMethods.eth_v1_beacon_headers_random_block_id_task: 1,
        EthConsensusMethods.eth_v1_node_version_task: 1,
    }
