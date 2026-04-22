import logging
from pathlib import Path

# third-party imports
from rich.console import Console

# own imports
from depsight.commands.scan.scan_widgets import ScanResultTableViewer
from depsight.utils.constants import COLOR_DIM_ORANGE, COLOR_PEACH, USER_DATA_DIR

logger = logging.getLogger(__name__)


def scan_handler(plugin, project_dir: str | Path, *, file: str | None = None, as_csv: bool = False):
    """Scan a project for dependencies using the given plugin.

    Invokes :pymethod:`plugin.collect` on *project_dir* to populate
    `plugin.dependencies`, then launches the Textual viewer.

    Parameters
    ----------
    plugin - An instantiated plugin that conforms to :class:`BasePlugin`.
    
    project_dir - Absolute path to the project root to scan.

    file - Optional dependency-file basename to scan. When ``None``,
        the plugin's :attr:`default_file` is used.

    as_csv - When `True`, export the results to a CSV file.
    """

    console = Console()

    target = file or plugin.default_file
    logger.info("Starting scan in '%s' with plugin '%s' (file='%s')", project_dir, plugin.name, target)
    console.print()
    console.print(
        f"Scanning [{COLOR_PEACH}]{project_dir}[/{COLOR_PEACH}] "
        f"using [{COLOR_DIM_ORANGE}]{plugin.name}[/{COLOR_DIM_ORANGE}] "
        f"→ [{COLOR_PEACH}]{target}[/{COLOR_PEACH}]"
    )
    console.print()

    # Collect dependencies using the plugin's collect() method
    logger.debug("Calling plugin.collect('%s', file='%s')", project_dir, target)
    plugin.collect(project_dir, file=target)
    logger.debug("Plugin returned %d dependency(ies)", len(plugin.dependencies))

    if not plugin.dependencies:
        logger.warning("No dependencies found in '%s' — lockfile may be missing or empty", project_dir)
        console.print("[yellow]No dependencies found.[/yellow]")
        return

    # Launch Textual app to display results
    viewer = ScanResultTableViewer(plugin.dependencies)
    logger.info("Rendering table with %d dependencies", len(plugin.dependencies))
    viewer.run()

    # Optionally export results to CSV using the plugin's export() method
    if as_csv:
        csv_path = plugin.export(project_dir, USER_DATA_DIR)
        logger.info("CSV exported to '%s'", csv_path)
        console.print(f"\n[{COLOR_PEACH}]CSV exported to[/{COLOR_PEACH}] [{COLOR_DIM_ORANGE}]{csv_path}[/{COLOR_DIM_ORANGE}]")