# Creating Custom Profiles

## Introduction

A profile is a collection of tasks that are executed during the benchmark. Each profile is a Python file that contains a class that inherits from the `chainbench.user.base.BaseUser` class.
The folder where the profiles are located is `chainbench/profile`. Each profile is located in a subfolder named after the blockchain/protocol that it is designed for.
For example, the `Oasis` profile is located in the [`chainbench/profile/oasis/general.py`](../chainbench/profile/oasis/general.py) file.

## Creating a Profile

Let's create a profile for the Oasis blockchain. We will use the `Oasis` profile as a reference.

### Step 1: Create a new file in the `profile` directory

Let's create a new file called `oasis.py` in the `chainbench/profile/oasis/` directory and add the following code:

```python
from chainbench.user import EvmUser


class OasisProfile(EvmUser):
    pass
```

We inherit `EvmUser` because it contains methods for benchmarking an EVM-based blockchain.

### Step 2: Configure wait time
`EvmUser` is a subclass of `FastHttpUser` from the [Locust](https://docs.locust.io/en/stable/) library. So defining wait time is straightforward.
Here we use `constant_pacing` to set a dynamic wait time between requests. 
The wait time is calculated as `n - response_time` where `n` is the value passed to `constant_pacing`.
If response time is greater than `n`, then the wait time is set to 0, and the next request is sent immediately once the previous one is finished.

There are other ways to set wait time, see the [Locust docs](https://docs.locust.io/en/stable/writing-a-locustfile.html#wait-time-attribute) for more details.

```python
from chainbench.user import EvmUser
from locust import constant_pacing


class OasisProfile(EvmUser):
    wait_time = constant_pacing(1)
```

### Step 3: Add `get_block_by_number` task

In a standard Locust test, `on_start` event will need to be used to fetch blockchain data before the test starts.
But `EvmUser` comes with `EvmTestData` class that handles this. Basically, before each worker starts spawning users
it fetches real blockchain data and stores it in memory, so it can be used for test data randomization.

When Locust "on_init" event occurs, `EvmTestData` fetches the chain ID, and gets the block range from which to fetch test data based on the chain ID.
The starting block is defined in the [`chainbench/test_data/evm.py`](../chainbench/test_data/evm.py) file for each supported protocol.
After that, blockchain data such as block numbers, block hashes, transactions, transaction hashes and addresses are fetched from the blockchain node and stored in memory.

```python
from chainbench.user import EvmUser
from chainbench.util.rng import get_rng
from locust import task, constant_pacing


class OasisProfile(EvmUser):
    wait_time = constant_pacing(2)

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        ),
```

`make_call` is a method from `EvmUser` that sends a request to the blockchain node and checks the response.
`_block_by_number_params_factory` returns a random list of parameters for the `eth_getBlockByNumber` method. 
`get_rng` is a helper function that returns a random number generator unique to the function that it is called in,
with a fixed seed. This is done to ensure that the same random number generator is used for the same function call, and
that the test data is consistent across all workers, as well as across multiple runs. This increases consistency of the data across runs, and makes them more comparable.
See the [`chainbench/user/evm.py`](../chainbench/user/protocol/evm.py) file for all supported param factories.

### Step 4: Add `get_syncing` task

Adding task for a call with static parameters is as simple as:

```python
from chainbench.user import EvmUser
from chainbench.util.rng import get_rng
from locust import task, constant_pacing


class OasisProfile(EvmUser):
    wait_time = constant_pacing(2)

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        ),

    @task
    def get_syncing_task(self):
        self.make_rpc_call(
            name="get_syncing",
            method="eth_syncing",
        ),

```

In case of `eth_syncing` we can omit the `params` argument because it doesn't have any parameters.

Here's an example of `eth_call` call with static parameters from [BSC profile](../chainbench/profile/bsc/general.py):

```python
from chainbench.user import EvmUser
from locust import task


class BscProfile(EvmUser):
    @task(100)
    def call_task(self):
        self.make_rpc_call(
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

### Step 5: Add `get_transaction_by_hash` task

For `eth_getTransactionByHash` we can use the `_transaction_by_hash_params_factory` method:

```python
from chainbench.user import EvmUser
from chainbench.util.rng import get_rng
from locust import task, constant_pacing


class OasisProfile(EvmUser):
    wait_time = constant_pacing(2)

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_rpc_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task
    def get_syncing_task(self):
        self.make_rpc_call(
            name="get_syncing",
            method="eth_syncing",
        ),
```

### Step 6: Add `get_code`, `get_balance`, and `get_transaction_cound` tasks

`eth_getCode`, `eth_getBalance`, and `eth_getTransactionCount` share the same parameters format, so we can use the `_get_balance_params_factory` method:

```python
from chainbench.user import EvmUser
from chainbench.util.rng import get_rng
from locust import task, constant_pacing


class OasisProfile(EvmUser):
    wait_time = constant_pacing(2)

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        ),

    @task
    def get_balance_task(self):
        self.make_rpc_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory(get_rng()),
        ),

    @task
    def get_transaction_count_task(self):
        self.make_rpc_call(
            name="get_transaction_count",
            method="eth_getTransactionCount",
            params=self._get_balance_params_factory(get_rng()),
        ),

    @task
    def get_code_task(self):
        self.make_rpc_call(
            name="get_code",
            method="eth_getCode",
            params=self._get_balance_params_factory(get_rng()),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_rpc_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task
    def get_syncing_task(self):
        self.make_rpc_call(
            name="get_syncing",
            method="eth_syncing",
        ),
```

### Step 7: Add the rest of the tasks

Here's the final version of the profile:

```python
from chainbench.user import EvmUser
from chainbench.util.rng import get_rng
from locust import task, constant_pacing


class OasisProfile(EvmUser):
    wait_time = constant_pacing(2)

    @task
    def get_block_by_number_task(self):
        self.make_rpc_call(
            name="get_block_by_number",
            method="eth_getBlockByNumber",
            params=self._block_params_factory(),
        ),

    @task
    def get_balance_task(self):
        self.make_rpc_call(
            name="get_balance",
            method="eth_getBalance",
            params=self._get_balance_params_factory(get_rng()),
        ),

    @task
    def get_transaction_count_task(self):
        self.make_rpc_call(
            name="get_transaction_count",
            method="eth_getTransactionCount",
            params=self._get_balance_params_factory(get_rng()),
        ),

    @task
    def get_code_task(self):
        self.make_rpc_call(
            name="get_code",
            method="eth_getCode",
            params=self._get_balance_params_factory(get_rng()),
        ),

    @task
    def get_transaction_by_hash_task(self):
        self.make_rpc_call(
            name="get_transaction_by_hash",
            method="eth_getTransactionByHash",
            params=self._transaction_by_hash_params_factory(get_rng()),
        ),

    @task
    def get_block_number_task(self):
        self.make_rpc_call(
            name="block_number",
            method="eth_blockNumber",
        ),

    @task
    def get_syncing_task(self):
        self.make_rpc_call(
            name="get_syncing",
            method="eth_syncing",
        ),

    @task
    def get_block_transaction_count_by_number_task(self):
        self.make_rpc_call(
            name="get_block_transaction_count_by_number",
            method="eth_getBlockTransactionCountByNumber",
            params=self._random_block_number_params_factory(get_rng()),
        ),
```

You can also find the full version of the profile [here](../chainbench/profile/oasis/general.py).

### Step 8: Run the benchmark

Now we can run the benchmark:

```bash
python3 -m chainbench start --profile oasis.general --users 50 --workers 2 --test-time 1h --target https://node-url --headless --autoquit
```
