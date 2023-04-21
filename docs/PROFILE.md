# Creating Custom Profiles

## Introduction

A profile is a python module that defines methods used for benchmarking a specific blockchain. It is located in the `chainbench/profiles` directory. 
The module name should be the same as the profile name. 
For example, the `ethereum` profile is located in the [`chainbench/profile/ethereum.py`](../chainbench/profile/ethereum.py) file.

## Creating a Profile

Here's the locustfile for Oasis that we will use as an example for creating a custom profile:

```python
import random
import secrets
from locust import task, between, HttpUser


class QuickstartUser(HttpUser):
    wait_time = between(0.1, 1.5)
    latest_block = 0
    latest_block_number = 0
    tx_hashes = ''

    def on_start(self):
        self.latest_block = self.client.post(
            '/', json=self._make_rpc_payload('eth_getBlockByNumber', ['latest', False])
        ).json()['result']
        self.latest_block_number = int(self.latest_block['number'], base=16)

    @staticmethod
    def _make_rpc_payload(method: str, params: list = None) -> dict:
        if not params:
            params = []

        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 0
        }

    def _get_random_block(self) -> str:
        return hex(random.randint(1, self.latest_block_number))

    def _get_random_address(self) -> str:
        return f'0x{secrets.token_hex(20)}'

    @task
    def get_block_by_number(self) -> dict:
        return self.client.post(
            '/', json=self._make_rpc_payload(
                "eth_getBlockByNumber",
                params=[self._get_random_block(), False]
            )
        ).json()

    @task
    def get_transaction_count(self):
        self.client.post(
            '/', json=self._make_rpc_payload(
                "eth_getTransactionCount",
                params=[self._get_random_address(), self._get_random_block()]
            )
        )

    @task
    def get_balance(self):
        self.client.post(
            '/', json=self._make_rpc_payload(
                "eth_getBalance",
                params=[self._get_random_address(), self._get_random_block()]
            )
        )

    def _get_random_tx_hash(self) -> str:
        return random.choice(self.get_block_by_number()['result']['transactions'])

    @task
    def get_transaction_by_hash(self):
        self.client.post(
            '/', json=self._make_rpc_payload(
                "eth_getTransactionByHash",
                params=[self._get_random_tx_hash()]
            )
        )

    @task
    def get_block_number(self):
        self.client.post('/', json=self._make_rpc_payload('eth_blockNumber'))

    @task
    def get_code(self):
        self.client.post(
            '/', json=self._make_rpc_payload(
                "eth_getCode",
                params=[self._get_random_address(), self._get_random_block()]
            )
        )

    @task
    def get_syncing(self):
        self.client.post('/', json=self._make_rpc_payload("eth_syncing"))

    @task
    def get_block_transaction_count_by_number(self):
        self.client.post(
            '/', json=self._make_rpc_payload(
                "eth_getBlockTransactionCountByNumber",
                params=[self._get_random_block()])
        )
```
### Step 1: Create a new file in the `profile` directory

Let's create a new file called `oasis.py` in the `chainbench/profile` directory and add the following code:

```python
from chainbench.user.evm import EVMBenchUser


class OasisProfile(EVMBenchUser):
    pass
```

We inherit `EVMBenchUser` because it contains methods for benchmarking an EVM-based blockchain.

### Step 2: Add the profile to the list of available profiles

In the [`chainbench/main.py`](../chainbench/main.py) file, add the profile name to the `PROFILES` list:

```python
PROFILES = [
    "avalanche",
    "bsc",
    "ethereum",
    "polygon",
    "oasis",
]
```

### Step 3: Configure wait time
`EVMBenchUser` is a subclass of `FastHttpUser` from the [Locust](https://docs.locust.io/en/stable/) library. So defining wait time is straightforward:

```python
from chainbench.user.evm import EVMBenchUser
from locust import between

class OasisProfile(EVMBenchUser):
    wait_time = between(0.1, 1.5)
```

### Step 4: Add `get_block_by_number` task

`on_start` in the original locustfile is used to get the latest block number and the latest block. 
But `EVMBenchUser` comes with `EVMTestData` class that handles this. Basically, before each worker starts spawning users
it fetches real blockchain data and stores it in memory, so it can be used for test data randomization.

Other methods such as `_make_rpc_payload`, `_get_random_block`, and `_get_random_address` also have their counterparts 
in `EVMTestData` class.

Here's the equivalent for `get_block_by_number` from the original locustfile:

```python
from chainbench.user.evm import EVMBenchUser
from locust import task, between


class OasisProfile(EVMBenchUser):
    wait_time = between(0.1, 1.5)
    
    @task
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),
```

`make_call` is a method from `EVMBenchUser` that sends a request to the blockchain node and checks the response.
`_block_by_number_params_factory` returns a random list of parameters for the `eth_getBlockByNumber` method. See the 
[`chainbench/user/evm.py`](../chainbench/user/evm.py) file for all supported param factories.

### Step 5: Add `get_syncing` task

Adding task for a call with static parameters is as simple as:

```python
from chainbench.user.evm import EVMBenchUser
from locust import task, between


class OasisProfile(EVMBenchUser):
    wait_time = between(0.1, 1.5)
    
    @task
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),
        
    @task
    def get_syncing_task(self):
        self.make_call(
            name="get_syncing",
            method="eth_syncing",
        ),

```

In case of `eth_syncing` we can omit the `params` argument because it doesn't have any parameters.

Here's an example of `eth_call` call with static parameters from [BSC profile](../chainbench/profile/bsc.py):

```python
class BscProfile(EVMBenchUser):
    @task(100)
    def call_task(self):
        self.make_call(
            name="call",
            method="eth_call",
            params=[
                {
                    "to": "0x55d398326f99059fF775485246999027B3197955",
                    "data": "0x70a08231000000000000000000000000f977814e90da44bfa03b6295a0616a897441acec",
                },
                "latest",
            ],
        ),
```
If we want tasks to have different weights, we can use the `@task` decorator with a weight argument.

### Step 6: Add `get_transaction_by_hash` task

For `eth_getTransactionByHash` we can use the `_transaction_by_hash_params_factory` method:

```python
from chainbench.user.evm import EVMBenchUser
from locust import task, between


class OasisProfile(EVMBenchUser):
    wait_time = between(0.1, 1.5)

    @task
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),
        
    @task
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task
    def get_syncing_task(self):
        self.make_call(
            name="get_syncing",
            method="eth_syncing",
        ),
```

### Step 7: Add `get_code`, `get_balance`, and `get_transaction_cound` tasks

`eth_getCode`, `eth_getBalance`, and `eth_getTransactionCount` share the same parameters format, so we can use the `_get_balance_params_factory` method:

```python
from chainbench.user.evm import EVMBenchUser
from locust import task, between


class OasisProfile(EVMBenchUser):
    wait_time = between(0.1, 1.5)

    @task
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),
        
    @task
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_transaction_count_task(self):
        self.make_call(
            name="get_transaction_count",
            method="eth_getTransactionCount",
            params=self._get_balance_params_factory(),
        ),
        
    @task
    def get_code_task(self):
        self.make_call(
            name="get_code",
            method="eth_getCode",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(),
        ),

    @task
    def get_syncing_task(self):
        self.make_call(
            name="get_syncing",
            method="eth_syncing",
        ),
```

### Step 8: Add the rest of the tasks

Here's the final version of the profile:

```python
from chainbench.user.evm import EVMBenchUser
from locust import task, between


class OasisProfile(EVMBenchUser):
    wait_time = between(0.1, 1.5)

    @task
    def get_block_by_number_task(self):
        self.make_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_by_number_params_factory(),
        ),

    @task
    def get_balance_task(self):
        self.make_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_transaction_count_task(self):
        self.make_call(
            name="get_transaction_count",
            method="eth_getTransactionCount",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_code_task(self):
        self.make_call(
            name="get_code",
            method="eth_getCode",
            params=self._get_balance_params_factory(),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(),
        ),
        
    @task
    def get_block_number_task(self):
        self.make_call(
            name="block_number",
            method="eth_blockNumber",
        ),

    @task
    def get_syncing_task(self):
        self.make_call(
            name="get_syncing",
            method="eth_syncing",
        ),

    @task
    def get_block_transaction_count_by_number_task(self):
        self.make_call(
            name="get_block_transaction_count_by_number",
            method="eth_getBlockTransactionCountByNumber",
            params=self._random_block_number_params_factory(),
        ),
```

You can find the full version of the profile [here](../chainbench/profile/oasis.py).
