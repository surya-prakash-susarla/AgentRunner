import logging

import typer
from dotenv import load_dotenv
from rich.console import Console

from src.config.config_handler import edit_config, get_config
from src.runner.root_runner import create_root_runner
from src.tools.mcp_master import get_mcp_master
from src.utils.cleanup import cleanup_manager
from src.utils.logging_config import setup_logger

# Set up logging for the main module
logger = setup_logger(__name__, logging.INFO)

# Initialize typer app
app = typer.Typer(
    name="replica-llm",
    help="A CLI tool for running and managing LLM agents",
    add_completion=True,
)

console = Console()


def initialize() -> None:
    # Initialize the config files and config file handler.
    get_config()

    # Initialize mcp tool handler
    get_mcp_master()


@app.command()
def chat():
    """Start an interactive chat session with an LLM agent"""
    runner = None
    try:
        # Create and set up the root runner
        runner = create_root_runner()
        if not runner:
            raise Exception("Failed to create root runner")

        cleanup_manager.register_runner(runner)

        # Main chat loop
        console.print(
            "[green]Starting chat session. Type 'exit' or 'quit' to end.[/green]"
        )
        while True:
            query = console.input("[bold blue]You:[/bold blue] ")
            if query.lower() in ["exit", "quit"]:
                console.print("[yellow]Chat session ended by user[/yellow]")
                break
            response = runner.getResponse(query)
            console.print(f"[bold green]Assistant:[/bold green] {response}")
    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Received keyboard interrupt, shutting down...[/yellow]"
        )
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
    finally:
        if runner:
            cleanup_manager.cleanup_all_processes()


@app.command()
def config() -> None:
    """Edit the configuration file in your default editor"""
    try:
        edit_config()
        console.print("[green]Configuration updated successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error editing configuration: {str(e)}[/red]")


def main() -> None:
    load_dotenv()
    initialize()
    app()
