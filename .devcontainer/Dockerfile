ARG PYTHON_VERSION="3.12"
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

# Install uv (fast Python package manager)
ARG UV_VERSION="0.11.1"
COPY --from=ghcr.io/astral-sh/uv:${UV_VERSION} /uv /uvx /usr/local/bin/

# Prevent Python stdout buffering
ENV PYTHONUNBUFFERED=1

# App environment
ENV APP_NAME=DEPSIGHT
ENV DEPSIGHT_ENV=development

# MkDocs dev server port
EXPOSE 8000
