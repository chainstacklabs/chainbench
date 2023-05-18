FROM python:3.10-buster

# copy files
COPY . /app
WORKDIR /app

# install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.4.0 python3 -
RUN $HOME/.local/bin/poetry config virtualenvs.create false

# install chainbench
RUN $HOME/.local/bin/poetry install --without dev
