# uv — Python Package Manager

Depsight uses [**uv**](https://docs.astral.sh/uv/) instead of pip for dependency management. uv is a Python package manager written in Rust that is significantly faster and provides a lockfile-based workflow similar to npm or cargo.

---

## Common Commands

```bash
# Install all dependencies (including dev and docs groups)
uv sync --all-groups

# Add a new runtime dependency
uv add <package>

# Add a dev dependency
uv add --group dev <package>

# Build a distributable wheel
uv build

# Run a command inside the managed environment
uv run depsight --help
```

---

## Lockfile

Running `uv sync` generates a `uv.lock` file that pins exact versions of every transitive dependency. This file is committed to version control to ensure reproducible installs across all environments — local, CI, and production.

The lockfile is a TOML file containing `[[package]]` sections for each resolved dependency:

```toml
[[package]]
name = "click"
version = "8.3.1"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "rich"
version = "13.9.4"
source = { registry = "https://pypi.org/simple" }
```

---

## Dependency Groups

Dependencies are declared in `pyproject.toml` using standard Python packaging metadata. Depsight defines three groups:

```toml
[project]
dependencies = [
    "click>=8.1.7",
    "rich>=13.7.0",
    "rich-click>=1.7.0",
]

[dependency-groups]
dev = [
    "mypy>=1.10",
    "pytest>=8.0",
    "ruff>=0.4",
]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.5",
    "mkdocs-mermaid2-plugin>=1.1",
]
```

| Group | Contents | Installed by |
|-------|----------|-------------|
| **Runtime** | Click, Rich, rich-click | `uv sync` |
| **Dev** | Ruff, mypy, pytest | `uv sync --group dev` |
| **Docs** | MkDocs, Material theme, Mermaid | `uv sync --group docs` |
| **All** | Everything above | `uv sync --all-groups` |
