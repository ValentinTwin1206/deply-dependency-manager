import logging

# third-party imports
from rich.console import Console

# own imports
from deply.commands.scan.scan_widgets import ScanResultTableViewer
from deply.utils.constants import COLOR_DIM_ORANGE, COLOR_PEACH


def scan_handler(plugin, project_dir: str, logger: logging.Logger):
    """Scan a project for dependencies using the given plugin.

    Invokes :pymethod:`plugin.collect` on *project_dir* to populate
    `plugin.dependencies`, then renders a Rich table to the console.

    Parameters
    ----------
    plugin - An instantiated plugin that conforms to :class:`BasePlugin`.
    
    project_dir - Absolute path to the project root to scan.
    
    logger - Logger instance provided by the run handler.
    """

    console = Console()

    logger.info("Starting scan in '%s' with plugin '%s'", project_dir, plugin.name)
    console.print()
    console.print(f"Scanning [{COLOR_PEACH}]{project_dir}[/{COLOR_PEACH}] using [{COLOR_DIM_ORANGE}]{plugin.name}[/{COLOR_DIM_ORANGE}]")
    console.print()

    logger.debug("Calling plugin.collect('%s')", project_dir)
    plugin.collect(project_dir)
    logger.debug("Plugin returned %d dependency(ies)", len(plugin.dependencies))

    if not plugin.dependencies:
        logger.warning("No dependencies found in '%s' — lockfile may be missing or empty", project_dir)
        console.print("[yellow]No dependencies found.[/yellow]")
        return

    viewer = ScanResultTableViewer(plugin.dependencies)

    logger.info("Rendering table with %d dependencies", len(plugin.dependencies))
    console.print(viewer)