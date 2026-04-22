from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from dataclasses import fields
from pathlib import Path

# own imports
from depsight.core.plugins.dependency import Dependency


class BasePlugin(ABC):
    """Abstract base class for depsight plugins.

    Subclasses must implement :attr:`name` and :meth:`collect`.
    A concrete :meth:`export` implementation is provided and shared
    by all plugins.

    Attributes
    ----------
    name:
        Human-readable identifier for the plugin (e.g. `"uv"`).
    """

    dependencies: list[Dependency]

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the canonical name of the package manager."""

    @property
    @abstractmethod
    def dependency_files(self) -> tuple[str, ...]:
        """Return every filename this plugin knows how to parse.

        The returned tuple lists the accepted lockfile / manifest
        basenames (e.g. ``("uv.lock", "pylock.toml")``). Used by the
        CLI to validate the value of ``--file`` and by :meth:`collect`
        to locate a source file when none was explicitly requested.
        """

    @property
    def default_file(self) -> str:
        """Filename used by :meth:`collect` when no file is specified.

        Defaults to the first entry of :attr:`dependency_files`.
        Plugins may override this when they want to prefer a different
        file from the tuple (for example, ``pylock.toml`` over ``uv.lock``).

        Returns
        -------
        str
            The basename of the file used when ``--file`` is omitted.
        """
        return self.dependency_files[0]

    @abstractmethod
    def collect(self, path: str | Path, file: str | None = None) -> None:
        """Populate *self.dependencies* from files found at *path*.

        Parameters
        ----------
        path - Absolute path to the project root to scan.

        file - Optional basename of the dependency file to parse.
            When ``None``, :attr:`default_file` is used. The value must
            be present in :attr:`dependency_files`.
        """

    def export(self, project_dir: str | Path, output_dir: str | Path) -> Path:
        """Export *self.dependencies* to a CSV file.

        The file is named `<plugin_name>_<project_dir_name>.csv`.

        Parameters
        ----------
        project_dir - The project root whose basename is used in the filename.

        output_dir - Directory where the CSV file will be written.

        Returns
        -------
        Path
            Absolute path to the created CSV file.
        """
        project_name = Path(project_dir).resolve().name
        dest = Path(output_dir)

        dest.mkdir(parents=True, exist_ok=True)
        csv_path = dest / f"{self.name}_{project_name}.csv"

        header = [f.name for f in fields(Dependency)]
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            for dep in self.dependencies:
                writer.writerow(getattr(dep, col) for col in header)

        return csv_path
