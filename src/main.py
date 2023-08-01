"""
Here we want to register the commands for the click app, serve the basic version and help
commands and execute the click app from the CLI arguments.
"""

from cli import cli
# noinspection PyUnresolvedReferences
import commands.analyse_data
# noinspection PyUnresolvedReferences
import commands.list_habits
# noinspection PyUnresolvedReferences
import commands.create_habit
# noinspection PyUnresolvedReferences
import commands.complete_task
# noinspection PyUnresolvedReferences
import commands.delete_habit
# noinspection PyUnresolvedReferences
import commands.sync_tasks

if __name__ == "__main__":
    # Greeting message
    cli()
