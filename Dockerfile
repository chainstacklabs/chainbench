# chainbench-grpc (Solana Yellowstone gRPC tool) build stage.
# Builds the Rust binary from a pinned ref so `chainbench grpc` can shell out to
# it. protoc is vendored by the crate, so no extra system deps are needed.
# NOTE: assumes the repo is reachable anonymously. If it stays private, pass a
# token via BuildKit secret (`--mount=type=secret,id=gh_token`) instead.
FROM rust:1.90-bookworm AS grpc
ARG CHAINBENCH_GRPC_REF=v0.4.0
RUN git clone --depth 1 --branch "${CHAINBENCH_GRPC_REF}" \
      https://github.com/CSFeo/chainbench-grpc /src \
    && cd /src \
    && cargo build --release

# build stage
FROM python:3.10-bookworm AS venv

# copy files
COPY pyproject.toml poetry.lock ./
WORKDIR /app

# install poetry
ENV POETRY_VERSION=1.5.0
RUN curl -sSL https://install.python-poetry.org | python3 -

# The `--copies` option tells `venv` to copy libs and binaries
RUN python -m venv --copies /app/venv
RUN . /app/venv/bin/activate && $HOME/.local/bin/poetry install --no-directory --without dev --no-root --compile

# runtime stage
FROM python:3.10-slim-bookworm as prod

COPY --from=venv /app/venv /app/venv/
ENV PATH /app/venv/bin:$PATH

RUN apt-get update && apt-get install -y tini htop nano curl

# Bundle the chainbench-grpc binary on PATH (used by `chainbench grpc`).
COPY --from=grpc /src/target/release/chainbench-grpc /usr/local/bin/chainbench-grpc

WORKDIR /app
COPY . ./
RUN python -m pip install .

ENTRYPOINT ["/usr/bin/tini", "--", "chainbench"]
