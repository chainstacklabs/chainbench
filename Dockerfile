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

RUN apt-get update && apt-get install -y tini htop nano

WORKDIR /app
COPY . ./
RUN python -m pip install .

ENTRYPOINT ["/usr/bin/tini", "--", "chainbench"]
