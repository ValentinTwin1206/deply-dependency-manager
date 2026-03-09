from deply.core.base_plugins.base import BasePlugin


class UVPlugin(BasePlugin):
    def __init__(self):
        self.name = "uv"

    def collect_dependencies(self, path: str) -> list[tuple[str, str]]:
        # Logic to parse uv.lock or pyproject.toml would go here
        return [("rich", "13.7.0"), ("click", "8.1.7")]