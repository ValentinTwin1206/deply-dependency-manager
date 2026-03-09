import rich_click as click

from deply.core.run import run_handler
from deply.utils.constants import APP_BANNER, SUPPORTED_PLUGINS

# rich-click styling
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 2)
click.rich_click.HEADER_TEXT = APP_BANNER
click.rich_click.COMMAND_GROUPS = {
    "deply": [{"name": "Package Managers", "commands": list(SUPPORTED_PLUGINS.keys())}]
}


@click.group()
def main():
    """A modern TUI framework for scanning local project dependencies."""
    pass


def _register_plugin(plugin_name: str):
    """Register a plugin as a Click subgroup with its commands."""

    @main.group(plugin_name, help=f"Commands for the {plugin_name} plugin.")
    @click.pass_context
    def plugin_group(ctx):
        """Entry point for a plugin subgroup that stores the plugin name in the context."""
        ctx.ensure_object(dict)
        ctx.obj["plugin_name"] = plugin_name

    @plugin_group.command("scan")
    @click.option(
        "--project-dir",
        type=click.Path(exists=True),
        required=True,
        help="Path to the project."
    )
    @click.option(
        "--verbose",
        is_flag=True,
        help="Enable verbose logging."
    )
    @click.pass_context
    def scan_cmd(ctx, project_dir, verbose):
        """Scan project dependencies using the selected plugin."""
        run_handler(ctx.obj["plugin_name"], "scan", project_dir, verbose)


# Dynamically register all available plugins as CLI subgroups
for _name in SUPPORTED_PLUGINS:
    _register_plugin(_name)


if __name__ == "__main__":
    main()