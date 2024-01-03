# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.13
FROM python:${PYTHON_VERSION}-alpine as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

RUN pip install poetry==0.1.0

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/temp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY easebox ./easebox
COPY frontend ./frontend
RUN touch README.md

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    poetry install --no-root && rm -rf $POETRY_CACHE_DIR

ENTRYPOINT [ "poetry", "run", "python", "manage.py", "runserver" ]
