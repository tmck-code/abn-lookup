FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
    && apt install -y --no-install-recommends \
        curl git \
    && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
ENV UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

ADD pyproject.toml .
ADD uv.lock .

RUN uv sync --all-groups

ADD . .