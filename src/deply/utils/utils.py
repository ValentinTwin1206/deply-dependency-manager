from __future__ import annotations

import importlib.metadata
import logging

from pathlib import Path

# own imports
from deply.core.base_plugins.base import BasePlugin

def discover_plugins(builtin_plugins: dict[str, type[BasePlugin]] = None) -> dict[str, type[BasePlugin]]:
    """Build the full plugin registry.

    Merges built-in plugins with any third-party plugins registered under
    the `deply.plugins` entry-point group.  Third-party plugins that
    collide with a built-in name are skipped with a warning.
    """

    registry: dict[str, type[BasePlugin]] = dict(builtin_plugins)

    eps = importlib.metadata.entry_points(group="deply.plugins")
    for ep in eps:
        if ep.name in builtin_plugins:
            # Built-in plugins are already registered via their entry-point;
            # skip to avoid duplicate instantiation.
            continue
        try:
            plugin_cls = ep.load()
            if not issubclass(plugin_cls, BasePlugin):
                continue
            registry[ep.name] = plugin_cls
        except Exception:
            raise SystemExit(f"Failed to load plugin '{ep.name}'.")

    return registry


def resolve_user_dir(app_name: str, *, dev_mode: bool) -> Path:
    """Return the user-level base directory for DepDex.

    Parameters
    ----------
    app_name:
        Application name (used to build `~/.{app_name}`).
    dev_mode:
        If `True`, return the repository root directory.

    Returns
    -------
    Path
        The resolved user-level directory path.
    """
    if dev_mode:
        return Path(__file__).resolve().parents[3] / f".{app_name}"
    return Path.home() / f".{app_name}"