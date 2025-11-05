# AGENTS Guidelines for This Repository

This repository contains Chainbench, a blockchain infrastructure benchmarking tool built on Locust. When working on the project interactively with an agent (e.g. the Codex CLI) please follow the guidelines below for efficient development and testing.

## 1. Use Headless Mode for Development Testing

* **Always use headless mode** with short test durations during development.
* **Start with minimal load** (few users, low spawn rate) to validate changes.
* **Do _not_ run long-duration tests** during agent development sessions.
* **Use `--autoquit`** flag to ensure tests terminate properly.

Example test command:
```bash
poetry run chainbench start --profile evm.light --users 5 --workers 1 --test-time 30s --target https://test-node --headless --autoquit
```

## 2. Keep Dependencies in Sync

If you add or update dependencies:

1. Use Poetry to manage dependencies: `poetry add <package>` or `poetry add --group dev <package>`.
2. Run `poetry lock --no-update` to update the lock file.
3. Install updated dependencies with `poetry install`.
4. Verify compatibility with Python 3.10+ as specified in the project.

## 3. Coding Conventions

* Follow Black formatting (120-character line length).
* Use isort for import sorting (Black-compatible profile).
* Follow Flake8 linting rules (ignore E203 and W503 for Black compatibility).
* Use type hints where appropriate.
* Keep MyPy checks passing.

## 4. Code Quality Checks

Before completing any task, run these quality checks:

| Command                  | Purpose                          |
| ------------------------ |----------------------------------|
| `poetry run black .`     | Format code to project standards |
| `poetry run isort .`     | Sort imports                     |
| `poetry run flake8`      | Run linting checks               |
| `poetry run mypy .`      | Run type checks                  |

Or use pre-commit hooks:
```bash
poetry run pre-commit run --all-files
```
If running pre-commit hooks for the first time, run this first:
```bash
poetry run pre-commit install
```

## 5. Testing Guidelines

Test changes progressively:

1. **Unit testing**: Test individual user classes and methods
2. **Profile validation**: Verify profiles load correctly
   ```bash
   poetry run chainbench list profiles
   ```
3. **Short headless tests**: Run brief tests with minimal load
4. **Method discovery**: Test endpoint compatibility
   ```bash
   poetry run chainbench discover https://test-node --clients geth
   ```

## 6. Profile Development

When creating or modifying profiles:

* Place custom profiles in the canonical directory: `chainbench/profile/<network>/…`
* Follow existing profile structure and conventions.
* Include docstrings explaining profile purpose.
* Test with small data sizes first (`--size XS`).
* Validate against multiple node types when applicable.

## 7. Working with Test Data

* Start with smallest data size (`--size XS`) for development.
* Use `--use-latest-blocks` for nodes with limited history.
* Consider using `--ref-url` for test data generation from a reference node.
* Monitor memory usage with larger data sizes.

## 8. Development Workflow

1. Make changes to source code
2. Run formatting: `poetry run black . && poetry run isort .`
3. Run linting: `poetry run flake8`
4. Run type checking: `poetry run mypy .`
5. Test with minimal profile first
6. Gradually increase complexity and load

## 9. Useful Commands Recap

| Command                                          | Purpose                               |
| ------------------------------------------------ | ------------------------------------- |
| `poetry install`                                 | Install all dependencies              |
| `poetry run chainbench --help`                   | Show all available commands           |
| `poetry run chainbench start --help`             | Show options for running a benchmark  |
| `poetry run chainbench --version`                | Show CLI version                      |
| `poetry run chainbench list methods`             | List supported RPC methods            |
| `poetry run chainbench list profiles`            | List available profiles               |
| `poetry run chainbench list shapes`              | List load pattern shapes              |
| `poetry run chainbench discover <url>`           | Discover available methods            |

## 10. Safety Reminders

* **Test against test/dev nodes first** before production nodes.
* **Monitor target node health** during benchmarks.
* **Use appropriate rate limits** to avoid overwhelming nodes.
* **Start with light profiles** before heavy ones.
* **Keep test durations short** during development.

---

Following these practices ensures reliable development, prevents overwhelming blockchain nodes, and maintains code quality. Always prioritize controlled testing and gradual load increases when benchmarking infrastructure.