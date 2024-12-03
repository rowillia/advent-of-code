ARG VARIANT="3.12"
ARG UV_VERSION=0.5.5

FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

ENV PYTHONDONTWRITEBYTECODE=True
ENV PYTHONUNBUFFERED=True
ENV UV_LINK_MODE=copy

COPY --from=uv --chown=vscode: /uv /uvx /bin/
