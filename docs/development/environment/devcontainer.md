# DevContainers

## About

A [DevContainer](https://containers.dev/) is a modern approach to virtualizing an entire development environment inside a Linux container. Instead of documenting setup steps in a README and hoping every contributor follows them correctly, a DevContainer defines and provisions the full environment as code automatically.

### Beyond Traditional Virtualization Techniques

Tools like `venv`, `pipenv`, and `virtualenv` isolate Python packages, and for many projects that is enough. DevContainers go further because they control the full operating system layer, not just Python. That makes them useful when a project depends on system tools, specific runtimes, or a development setup that should match CI. However, they might introduce some overhead, as developers need Docker or any other container manager installed and should understand the basics of working with containers. The table below shows when that extra complexity is worth it:

| Capability | venv / pipenv | DevContainer |
|-------------|:---:|:---:|
| Keep project packages separate from the system Python and other projects | ✅ | ✅ |
| Guarantee every developer uses the exact same Python interpreter version | ❌ | ✅ |
| Install OS-level libraries via `apt` (e.g. `gcc` for C extensions, `libpq` for Postgres) | ❌ | ✅ |
| Ship tools like `uv`, `ruff`, or Nuitka compiler dependencies inside the environment | ❌ | ✅ |
| Automatically install editor extensions and apply workspace settings for every developer | ❌ | ✅ |
| Run the exact same OS, Python, and toolchain locally as the CI pipeline | ❌ | ✅ |

---

### IDE Support

The [DevContainer specification](https://containers.dev/) is an open standard supported by multiple editors. VS Code supports it through the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), JetBrains IDEs connect through [Gateway](https://www.jetbrains.com/remote-development/gateway/), and the [`devcontainer` CLI](https://github.com/devcontainers/cli) enables headless usage in automation and CI pipelines.

Per-IDE configuration lives under the `customizations` key in `devcontainer.json`, so extensions and settings for different editors coexist in the same file without conflict. The `customizations` key is specific to IDEs like VS Code and JetBrains while the `devcontainer` CLI is a headless runner and ignores this section entirely. This is one of the biggest quality-of-life improvements DevContainers offer since every developer opens the project and immediately gets the right extensions, formatters, and IDE behaviour. There is no manual setup, no "works on my machine" differences.

```json
{
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",        // Python language support, IntelliSense, and debugging
                "charliermarsh.ruff",      // Fast linter and formatter — enforces code style on save
                "eamodio.gitlens"          // Inline Git blame, history, and branch comparisons
            ]
        },
        "jetbrains": {
            "plugins": [
                "com.intellij.python",     // Python language support and debugger
                "com.jetbrains.plugins.ini" // TOML / INI file support for pyproject.toml
            ]
        }
    }
}
```

---

## DevContainer Components

### `devcontainer.json`

`devcontainer.json` is the central configuration file. It tells the IDE how to build the container, what to install, and how to configure the workspace. Here is the full Depsight configuration with the most important entries explained:

#### Build Configuration

The `build` section points to the Dockerfile and passes build arguments. `${localEnv:...}` allows developers to override values via host environment variables, with defaults after the colon:

```json
{
    "name": "Depsight DevContainer",
    "build": {
        "context": "..",
        "dockerfile": "Dockerfile",
        "args": {
            "PYTHON_VERSION": "${localEnv:PYTHON_VERSION:3.12}",
            "UV_VERSION": "${localEnv:UV_VERSION:0.10.9}"
        }
    }
}
```

#### Environment Variables

`containerEnv` sets environment variables available inside the container. Depsight uses them to identify the application name and to enable development mode:

```json
{
    "containerEnv": {
        "APP_NAME": "DEPSIGHT",
        "DEPSIGHT_ENV": "development"
    }
}
```

#### Port Forwarding

`forwardPorts` exposes container ports to the host. Depsight forwards port 8000 for the MkDocs development server:

```json
{
    "forwardPorts": [8000],
    "portsAttributes": {
        "8000": {
            "label": "MkDocs Dev Server",
            "onAutoForward": "notify"
        }
    }
}
```

#### Lifecycle Commands

`postCreateCommand` runs once after the container is created. Depsight uses it to install all dependencies automatically:

```json
{
    "postCreateCommand": "uv sync --all-groups",
    "remoteUser": "vscode"
}
```

Other lifecycle hooks include `postStartCommand` (runs on every container start) and `postAttachCommand` (runs each time the IDE attaches).

---

### `Dockerfile`

#### Role of the Dockerfile

The `Dockerfile` defines the content of the container image like the pre-installed system tools, users, and their permissions, while `devcontainer.json` controls how the IDE integrates with that image and which lifecycle commands to run.

When `devcontainer.json` includes a `build` block, the IDE builds the image from the Dockerfile before starting the container. Without one, DevContainers use a pre-built image directly.

The `Dockerfile` of the Depsight's DevContainer is intentionally minimal. It extends the [Microsoft DevContainer base image](#microsofts-devcontainer-base-images), only installs `uv` and exposes certain environment variables.

```dockerfile
ARG PYTHON_VERSION="3.12"
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}

ARG UV_VERSION="0.10.9"
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh \
    | UV_INSTALL_DIR=/usr/local/bin sh

ENV PYTHONUNBUFFERED=1
ENV APP_NAME=DEPSIGHT
ENV DEPSIGHT_ENV=development

EXPOSE 8000
```

---

#### Microsoft's DevContainer Base Images

Microsoft publishes **purpose-built** base images at [`mcr.microsoft.com/devcontainers`](https://mcr.microsoft.com/en-us/catalog?search=devcontainers) for most common languages and stacks such as *Python*, *JavaScript*, *Rust*, etc. Unlike regular container images, these DevContainer images are built for development:

| Feature / Aspect                 | `python:3.12` | `mcr.microsoft.com/devcontainers/python:3.12` |
|----------------------------------|----------------------------------|--------------------------------------------|
| Default user                     | `root`                           | `vscode` with `sudo` access                       |
| Non-root workflow                | Manual setup required            | Ready out of the box                       |
| Preinstalled tools               | Minimal                          | Extensive        |
| Python tooling                   | `pip` only                       | `pip`, `pipx`, common dev tools            |
| Shell                            | `sh`, `bash` | `sh`, `bash`, `zsh` |
| VS Code integration              | Requires manually creating a non-root user and setting `remoteUser` | Works out of the box with pre-configured `vscode` user |
| VS Code Server                   | Permission issues with the default `root` user; requires manual non-root setup | Works seamlessly; `vscode` user is the default |
| Workspace setup                  | `/workspaces` folder owned by `root` | `/workspaces`  owned by `vscode` — no `USER` directive needed |

---

## CI/CD Integration

One of the biggest advantages of DevContainers is that the same container image used for local development can also be used in CI. This eliminates the classic problem of environment drift — builds that pass locally but fail in the pipeline because of a different OS, Python version, or missing system library.

The [`devcontainers/ci`](https://github.com/devcontainers/ci) GitHub Action makes this straightforward. It reads the project's `devcontainer.json`, builds the container, and runs commands inside it:

```yaml
- name: Run CI inside DevContainer
  uses: devcontainers/ci@v0.3
  with:
    configFile: .devcontainer/devcontainer.json
    runCmd: |
      # any commands here run inside the same container as local development
```

Depsight uses exactly this approach. The key step in `.github/workflows/build.yml` builds the DevContainer and runs linting, type checking, tests, and the wheel build all inside it:

```yaml
- name: Lint, test & build wheel
  uses: devcontainers/ci@v0.3
  with:
    configFile: .devcontainer/devcontainer.json
    runCmd: |
      set -e
      source .venv/bin/activate

      depsight --help                         # CLI health check
      ruff check src/ tests/                  # Linting
      mypy src/                               # Type checking
      python -m pytest tests/ -v --tb=short   # Tests
      uv build                                # Build wheel
```

`PYTHON_VERSION` and `UV_VERSION` are passed as Docker build arguments, so CI uses exactly the same Python and uv versions as the local DevContainer.
