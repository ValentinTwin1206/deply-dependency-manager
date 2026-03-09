FROM mcr.microsoft.com/devcontainers/python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Nuitka build dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        gcc \
        patchelf \
        ccache \
 && rm -rf /var/lib/apt/lists/*

# Keep Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set DepDex to development mode
ENV DEPDEX_ENV=development
ENV APP_NAME=DEPDEX

USER vscode