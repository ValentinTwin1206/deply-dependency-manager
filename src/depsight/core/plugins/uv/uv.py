from __future__ import annotations

import tomllib

from pathlib import Path

# own imports
from depsight.core.plugins.base import BasePlugin
from depsight.core.plugins.dependency import Dependency, packageType

class UVPlugin(BasePlugin):
    """Plugin for **uv**.

    Supports both the legacy `uv.lock` file and the PEP 751
    `pylock.toml` interoperable lockfile format.
    """

    def __init__(self) -> None:
        self.dependencies: list[Dependency] = []

    @property
    def name(self) -> str:
        return "uv"

    @property
    def dependency_files(self) -> tuple[str, ...]:
        return ("uv.lock", "pylock.toml")

    @property
    def default_file(self) -> str:
        """Use `uv.lock` by default; `pylock.toml` is opt-in via `--file`."""
        return "uv.lock"

    @staticmethod
    def _load_dependency_files(project_dir: Path, filename: str) -> tuple[dict, Path] | None:
        """Walk *project_dir* for *filename*, parse the first match as TOML.

        Checks the project root first, then walks subdirectories.
        Returns the parsed data and the resolved file path, or
        `None` if no matching file is found.
        """
        root_candidate = project_dir / filename
        if root_candidate.is_file():
            with root_candidate.open("rb") as f:
                return tomllib.load(f), root_candidate.resolve()

        for path in project_dir.rglob(filename):
            if path.is_file():
                with path.open("rb") as f:
                    return tomllib.load(f), path.resolve()

        return None

    #
    # METHODS
    # # # # # # #
    def collect(self, project_dir: str | Path, file: str | None = None) -> None:
        """Parse a uv lockfile and populate `self.dependencies`.

        Parameters
        ----------
        project_dir - Absolute path to the project root to scan.

        file - Optional lockfile basename to parse. Must be one of
            :attr:`dependency_files`. When `None`, :attr:`default_file`
            is used.

        Raises
        ------
        ValueError
            When *file* is not part of :attr:`dependency_files`.
        """
        target = file or self.default_file
        if target not in self.dependency_files:
            raise ValueError(
                f"Unsupported file '{target}' for plugin '{self.name}'. "
                f"Supported: {', '.join(self.dependency_files)}"
            )

        project_dir = Path(project_dir)

        result = self._load_dependency_files(project_dir, target)
        if result is None:
            self.dependencies = []
            return

        data, lockfile_path = result

        if target == "pylock.toml":
            self.dependencies = self._parse_pylock(data, lockfile_path)
        else:
            self.dependencies = self._parse_uv_lock(data, lockfile_path)

    def _parse_uv_lock(self, data: dict, lockfile_path: Path) -> list[Dependency]:
        """Parse the uv-specific `uv.lock` format."""
        lockfile_str = str(lockfile_path)
        packages: list[dict] = data.get("package", [])

        # Build name → version and name → registry lookups
        locked: dict[str, str] = {}
        sources: dict[str, str] = {}
        project_block: dict | None = None

        for pkg in packages:
            pkg_name = pkg.get("name", "")
            pkg_version = pkg.get("version", "")

            if pkg_name and pkg_version:
                locked[pkg_name] = pkg_version

            registry = pkg.get("source", {}).get("registry")
            if pkg_name and registry:
                sources[pkg_name] = registry  # PyPI URL or private index

            if "editable" in pkg.get("source", {}):
                project_block = pkg

        # No editable block → every locked package counts as runtime
        if project_block is None:
            return [
                Dependency(
                    name=n,
                    version=v,
                    tool_name=self.name,
                    registry=sources.get(n),
                    file=lockfile_str,
                )
                for n, v in sorted(locked.items())
            ]

        # Parse runtime deps
        runtime_names = [
            dep["name"] for dep in project_block.get("dependencies", [])
        ]

        # Classify non-runtime groups.
        # Both optional-dependencies and dev-dependencies are non-prod → "dev".

        non_runtime_names: set[str] = set()

        # [project.optional-dependencies]  →  uv.lock optional-dependencies
        for _group, group_deps in project_block.get("optional-dependencies", {}).items():
            non_runtime_names.update(dep["name"] for dep in group_deps)

        # PEP 735 [dependency-groups]  →  uv.lock dev-dependencies
        for _group, group_deps in project_block.get("dev-dependencies", {}).items():
            non_runtime_names.update(dep["name"] for dep in group_deps)

        # Parse version constraints from metadata.requires-dist
        metadata = project_block.get("metadata", {})
        constraints: dict[str, str] = {
            entry["name"]: entry["specifier"]
            for entry in metadata.get("requires-dist", [])
            if "specifier" in entry
        }

        # Parse version constraints from metadata.requires-dev
        for _group, entries in metadata.get("requires-dev", {}).items():
            for entry in entries:
                if "specifier" in entry:
                    constraints[entry["name"]] = entry["specifier"]

        # Build category lookup: prod for runtime, dev for everything else
        category_map: dict[str, packageType] = {}
        for dep_name in runtime_names:
            category_map[dep_name] = "prod"

        for dep_name in non_runtime_names:
            category_map.setdefault(dep_name, "dev")

        # Identify direct dependency names (all explicitly declared deps)
        direct_names: set[str] = set(runtime_names) | non_runtime_names

        # Build structured dependency list
        deps: list[Dependency] = [
            Dependency(
                name=dep_name,
                version=locked.get(dep_name),
                constraint=constraints.get(dep_name),
                tool_name=self.name,
                registry=sources.get(dep_name),
                file=lockfile_str,
                category=category_map.get(dep_name, "prod"),
                is_transitive=dep_name not in direct_names,
            )
            for dep_name in sorted(category_map)
        ]

        # Append transitive dependencies (locked but not declared directly)
        for dep_name in sorted(locked):
            if dep_name not in category_map and dep_name != project_block.get("name"):
                deps.append(
                    Dependency(
                        name=dep_name,
                        version=locked[dep_name],
                        tool_name=self.name,
                        registry=sources.get(dep_name),
                        file=lockfile_str,
                        category="prod",
                        is_transitive=True,
                    )
                )

        return deps

    def _parse_pylock(self, data: dict, lockfile_path: Path) -> list[Dependency]:
        """Parse a PEP 751 `pylock.toml` file.

        PEP 751 defines a minimal interoperable lockfile format. Packages
        are listed under `[[packages]]` with `name`, `version` and
        an optional `index` URL. The spec itself does not distinguish
        direct from transitive or prod from dev dependencies, so every
        entry is reported as `prod` with `is_transitive=False`.

        Parameters
        ----------
        data - Parsed TOML content of the `pylock.toml` file.

        lockfile_path - Absolute path to the lockfile (stored on each
            produced :class:`Dependency`).

        Returns
        -------
        list[Dependency]
            Dependencies listed in the lockfile, sorted by name.
        """
        lockfile_str = str(lockfile_path)
        packages: list[dict] = data.get("packages", [])

        deps: list[Dependency] = []
        for pkg in packages:
            pkg_name = pkg.get("name")
            if not pkg_name:
                continue
            deps.append(
                Dependency(
                    name=pkg_name,
                    version=pkg.get("version"),
                    tool_name=self.name,
                    registry=pkg.get("index"),
                    file=lockfile_str,
                    category="prod",
                    is_transitive=False,
                )
            )

        deps.sort(key=lambda d: d.name)
        return deps
