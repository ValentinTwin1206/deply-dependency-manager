FROM mcr.microsoft.com/devcontainers/python:3.12

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Nuitka build dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        make \
        patchelf \
        ccache \
        pkg-config \
 && rm -rf /var/lib/apt/lists/*

# Enable ccache for faster repeated builds
ENV CC="ccache gcc"
ENV CXX="ccache g++"

# Prevent Python stdout buffering
ENV PYTHONUNBUFFERED=1

# App environment
ENV APP_NAME=DEPLY
ENV DEPLY_ENV=development

# MkDocs dev server port
EXPOSE 8000

USER vscode