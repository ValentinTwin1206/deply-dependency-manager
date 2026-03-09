from rich.console import Console
from rich.table import Table
from deply.core.dependency import Dependency

console = Console()

def scan_handler(plugin, project_dir: str):
    console.print(f"[bold blue]Scanning project:[/bold blue] {project_dir} using [green]{plugin.name}[/green]...")
    
    raw_deps = plugin.collect_dependencies(project_dir)
    dependencies = [Dependency(name=n, version=v, tool_name=plugin.name) for n, v in raw_deps]

    table = Table(title="Project Dependencies")
    table.add_column("Package", style="cyan")
    table.add_column("Version", style="magenta")
    table.add_column("Source", style="green")

    for dep in dependencies:
        table.add_row(dep.name, dep.version, dep.tool_name)

    console.print(table)