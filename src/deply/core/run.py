import logging

# own imports
from deply.commands.scan import scan_handler
from deply.core.factory import PluginFactory
from deply.utils.logger import get_logger


def run_handler(plugin_name: str, command: str, project_dir: str, verbose: bool):
    """Resolve a plugin by name and execute the requested command.

    Uses :class:`~deply.core.factory.PluginFactory` to instantiate the plugin
    from the registry and dispatches the given `command` (e.g. `"scan"`).

    Parameters
    ----------
    plugin_name - Key in `PLUGIN_REGISTRY` identifying the plugin (e.g. `"uv"`).

    command - The action to perform. Currently supported: `"scan"`.

    project_dir - Path to the project directory to analyse.

    verbose - When `True`, enable debug-level logging.
    """
    
    log_level = logging.DEBUG if verbose else logging.INFO
    logger = get_logger(command, level=log_level)
    

    try:
        plugin = PluginFactory.create(plugin_name)
    except (ValueError, TypeError) as exc:
        logger.error(str(exc))
        return

    if command == "scan":
        scan_handler(plugin, project_dir)
    else:
        logger.error(f"Unknown command '{command}' for plugin '{plugin_name}'.")