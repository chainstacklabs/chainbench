<img width="1200" alt="Labs" src="https://user-images.githubusercontent.com/99700157/213291931-5a822628-5b8a-4768-980d-65f324985d32.png">

<p>
 <h3 align="center">Chainstack is the leading suite of services connecting developers with Web3 infrastructure</h3>
</p>

<p align="center">
  <a target="_blank" href="https://chainstack.com/build-better-with-ethereum/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Ethereum.svg" /></a>&nbsp;  
  <a target="_blank" href="https://chainstack.com/build-better-with-bnb-smart-chain/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/BNB.svg" /></a>&nbsp;
  <a target="_blank" href="https://chainstack.com/build-better-with-polygon/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Polygon.svg" /></a>&nbsp;
  <a target="_blank" href="https://chainstack.com/build-better-with-avalanche/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Avalanche.svg" /></a>&nbsp;
  <a target="_blank" href="https://chainstack.com/build-better-with-fantom/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Fantom.svg" /></a>&nbsp;
</p>

<p align="center">
  • <a target="_blank" href="https://chainstack.com/">Homepage</a> •
  <a target="_blank" href="https://chainstack.com/protocols/">Supported protocols</a> •
  <a target="_blank" href="https://chainstack.com/blog/">Chainstack blog</a> •
  <a target="_blank" href="https://docs.chainstack.com/quickstart/">Chainstack docs</a> •
  <a target="_blank" href="https://docs.chainstack.com/quickstart/">Blockchain API reference</a> • <br> 
  • <a target="_blank" href="https://console.chainstack.com/user/account/create">Start for free</a> •
</p>

# Chainbench
![checks status](https://github.com/chainstacklabs/chainbench/actions/workflows/checks.yml/badge.svg) 
![build status](https://github.com/chainstacklabs/chainbench/actions/workflows/python-publish.yml/badge.svg)
![version](https://img.shields.io/pypi/v/chainbench)
![license](https://img.shields.io/github/license/chainstacklabs/chainbench)

This project allows you to benchmark your blockchain infrastructure. It uses [Locust](https://docs.locust.io/en/stable/index.html) under the hood.

## Project Details

Chainbench lets you to easily define profiles for any EVM-compatible chain. 
You can use not only hard-coded values but also real chain data to generate dynamic call parameters.

Main features:
- Built-in profiles for Ethereum, Binance Smart Chain, Polygon, Oasis, and Avalanche
- Support for custom profiles
- Dynamic call params generation using real chain data
- Headless and web UI modes

Check out the [docs](docs/PROFILE.md) for more information about the profile creation.

## Prerequisites

- Python 3.10+
- Poetry 1.2+ (installation instructions [here](https://python-poetry.org/docs/#installation))

## Installation

### Using pip

```shell
pip install chainbench
```

After installation, you can run the tool using the following command:
```shell
chainbench start --help
```

### Using Poetry

Clone the repository:
```shell
git clone git@github.com:chainstacklabs/chainbench.git
```

Install dependencies:
```shell
cd chainbench && poetry install --without dev
```

When installing using Poetry, you can run the tool using the following command:
```shell
poetry run chainbench start --help
```

## Example Usage
All the examples below assume that you have installed the tool using `pip`. If you installed it using `poetry`, replace `chainbench` with `poetry run chainbench`.

To learn about the parameters and flags, run the following command:
```shell
chainbench start --help
```

Basic usage is:
```shell
chainbench start --profile bsc --users 50 --workers 2 --test-time 12h --target https://node-url --headless --autoquit
```

This will run a load test for BSC with 2 workers, 50 users and 12 hours test time in headless mode.
After the test is finished, the tool will automatically quit.

### Parameters and Flags
- `--profile`: This flag specifies the profile to use for the benchmark. Available profiles are `ethereum`, `bsc`, `polygon`, `oasis`, and `avalanche`.
- `--users`: This flag sets the number of simulated users to use for the benchmark.
- `--workers`: This flag sets the number of worker threads to use for the benchmark.
- `--test-time`: This flag sets the duration of the test to run.
- `--target`: This flag specifies the target blockchain node URL that the benchmark will connect to.
- `--headless`: This flag runs the benchmark in headless mode, meaning that no graphical user interface (GUI) will be displayed during the test. This is useful for running the test on a remote server or when the GUI is not needed.
- `--autoquit`: This flag tells the Chainbench tool to automatically quit after the test has finished. This is useful for running the benchmark in an automated environment where manual intervention is not desired.
- `--help`: This flag displays the help message.

### Profiles
Profiles are located in the [`profile`](chainbench/profile) directory. For a tutorial on how to create custom profiles, please refer to [this document](docs/PROFILE.md).

### Web UI Mode

Run the following command to run a load test for BSC in UI mode. It will start a web server on port 8089. 
Target is not required as you can specify it in the UI along with the number of users, spawn rate and test time.

```shell
chainbench start --profile bsc --workers 1
```

### Headless Mode

If you want to run a load test for BSC in headless mode, run the following command:

```shell
chainbench start --profile bsc --workers 4 --users 100 --test-time 1h --target https://node-url --headless --autoquit
```

It will run a load test for BSC with 4 workers, 100 users and 1 hour test time.

In practice, you will probably want to run the benchmark on a remote server. Here's the example utilizing `nohup`:

```shell
nohup chainbench start --profile bsc --workers 4 --users 100 --test-time 1h --target https://node-url --headless --autoquit &
```

## License
This project is licensed under the [Apache 2.0 License](LICENSE).