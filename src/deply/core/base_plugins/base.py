"""Base interface that every deply plugin must implement."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class BasePlugin(Protocol):
    """Contract for deply plugins.

    Any class that satisfies this protocol can be registered as a plugin,
    either as a built-in or via the ``deply.plugins`` entry-point group.

    Attributes
    ----------
    name:
        Human-readable identifier for the plugin (e.g. ``"uv"``).
    """

    name: str

    def collect_dependencies(self, path: str) -> list[tuple[str, str]]:
        """Return a list of ``(package_name, version)`` tuples found at *path*."""
        ...
