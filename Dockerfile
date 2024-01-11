# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.13
FROM python:${PYTHON_VERSION}-alpine as base

# python 
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip config
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/app/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    \
    PYSETUP_PATH="/app" \
    VENV_PATH="/app/pysetup/.venv" \
    POETRY_CACHE_DIR="/temp/poetry_cache"

ENV PATH="${POETRY_HOME}/bin:${VENV_PATH}/bin:$PATH"


FROM base as builder-base
RUN apk update && apk add --no-cache && apk add --update alpine-sdk
    
RUN curl -sSL https://install.python-poetry.org | python

WORKDIR $PYSETUP_PATH
COPY pyproject.toml poetry.lock ./

RUN touch README.md

RUN apk add musl-dev libpq-dev gcc &&\
    poetry install --no-dev --no-root && rm -rf $POETRY_CACHE_DIR

# development image
FROM base as development
WORKDIR $PYSETUP_PATH

COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

RUN poetry install --no-root && apk add libpq-dev

WORKDIR /app

COPY easebox ./easebox
COPY frontend ./frontend

EXPOSE 8000
