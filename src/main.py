import asyncio
import logging
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from fastmcp import Client, FastMCP
from rich import print
from rich.console import Console

from src.runner.gemini_runner import GeminiRunner
from src.tools.samples.server import echo_mcp_server
from src.tools.replicator_tools import replicator_tools_server
from src.utils.cleanup import cleanup_manager
from src.utils.logging_config import setup_logger
from src.config.config_handler import edit_config, get_config

# Set up logging for the main module
logger = setup_logger(__name__, logging.INFO)

# Initialize typer app
app = typer.Typer(
    name="replica-llm",
    help="A CLI tool for running and managing LLM agents",
    add_completion=True
)

console = Console()

def get_sample_client():
    # NOTE: A single client can contain multiple servers.
    tool_server = FastMCP("main_server")
    asyncio.run(tool_server.import_server("echo_tools", echo_mcp_server))
    asyncio.run(tool_server.import_server("replicator_tools", replicator_tools_server))
    return Client(tool_server)


@app.command()
def chat():
    get_config()
    """Start an interactive chat session with an LLM agent"""
    runner = None
    try:
        meta_instruction = '''
            You are the orchestrator agent in charge of managing specialized child agents. Your role is to chat naturally with the user, delegate tasks to child agents using available tools when appropriate, and manage their lifecycle if needed.

            You may:
            - Create child agents dynamically, choosing their names, types, and instructions if the user does not specify.
            - Route follow-up questions to relevant child agents based on their assigned roles.
            - Summarize or rephrase responses from child agents before replying to the user.
            - Proactively call tools and relay agent responses without waiting for user input when appropriate.

            Always behave as an intelligent, proactive assistant. Only pause for confirmation when ambiguity exists or user intent is unclear.
        '''

        # Get configuration and set up runner (to be handled by wrapper)
        runner = GeminiRunner(instruction=meta_instruction)
        runner.configureMcp(get_sample_client())
        cleanup_manager.register_runner(runner)

        # Main chat loop
        console.print("[green]Starting chat session. Type 'exit' or 'quit' to end.[/green]")
        while True:
            query = console.input("[bold blue]You:[/bold blue] ")
            if query.lower() in ["exit", "quit"]:
                console.print("[yellow]Chat session ended by user[/yellow]")
                break
            response = runner.getResponse(query)
            console.print(f"[bold green]Assistant:[/bold green] {response}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Received keyboard interrupt, shutting down...[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
    finally:
        if runner:
            cleanup_manager.cleanup_all_processes()


@app.command()
def config():
    """Edit the configuration file in your default editor"""
    try:
        edit_config()
        console.print("[green]Configuration updated successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error editing configuration: {str(e)}[/red]")


def main():
    load_dotenv()
    app()
