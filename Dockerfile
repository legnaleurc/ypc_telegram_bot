FROM python:3.12.2-slim-bookworm

# env
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.8.2

# setup poetry
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION
# add poetry to path
ENV PATH=$POETRY_HOME/bin:$PATH

WORKDIR /app
COPY . /app
RUN poetry install --only=main --no-root
