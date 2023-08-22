"""
Here we want to register the commands for the click app, serve the basic version and help
commands and execute the click app from the CLI arguments.
"""

from commands import *
from cli import cli

if __name__ == "__main__":
    # Greeting message
    cli()
