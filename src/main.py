"""
Here we want to register the commands for the click app, serve the basic version and help
commands and execute the click app from the CLI arguments.
"""

from commands import (
    analyse_data,
    delete_habit,
    create_habit,
    complete_task,
    list_habits,
    sync_tasks
)
from cli import cli

if __name__ == "__main__":
    # Greeting message
    cli()
