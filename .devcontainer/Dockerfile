ARG VARIANT="3.14"
ARG UV_VERSION=0.9.13

FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

ENV PYTHONDONTWRITEBYTECODE=True
ENV PYTHONUNBUFFERED=True
ENV UV_LINK_MODE=copy

COPY --from=uv --chown=vscode: /uv /uvx /bin/

# Install autoenv for automatic venv activation
RUN git clone https://github.com/hyperupcall/autoenv.git /home/vscode/.autoenv \
    && echo 'AUTOENV_ENV_FILENAME=.autoenv' >> /home/vscode/.zshrc \
    && echo 'AUTOENV_ENV_LEAVE_FILENAME=.autoenv.leave' >> /home/vscode/.zshrc \
    && echo 'AUTOENV_ENABLE_LEAVE=1' >> /home/vscode/.zshrc \
    && echo 'AUTOENV_ASSUME_YES=1' >> /home/vscode/.zshrc \
    && echo 'source /home/vscode/.autoenv/activate.sh' >> /home/vscode/.zshrc \
    && chown -R vscode:vscode /home/vscode/.autoenv
