"""
This command allows users to create a new habit, and in the process, it guides the users through
a series of prompts to get the correct information when creating the habit.
"""

import click

from cli import cli
from database import Habit, Periodicity


@cli.command()
def create_habit():
    """
    Create new habits here.

    This code defines a command-line interface (CLI) command called `create_habit`.
    When this command is executed, it prompts the user to enter a new habit name,
    a periodicity for the habit, and a task template for the habit. The
    periodicity is chosen from a list of predefined options, and the task
    template is a list of tasks that the user can add to.
    The `create_habit` function then calls the `create_habit` method of the
    `db` object, passing in the user's input as arguments.
    This method creates a new habit in the database with the specified name,
    periodicity, and task template.
    """
    name = click.prompt('Please enter a new Habit name', type=str)

    periodicity_options = [
        v.name for v in list(Periodicity)
    ]
    periodicity = click.prompt(
        'Please enter the habit Periodicity',
        type=click.Choice(periodicity_options, case_sensitive=False)
    )

    task_template = []
    while True:
        task_template.append(click.prompt('Please provide the task for your habit', type=str))
        if not click.confirm('Do you want to add more tasks?'):
            break
    Habit(name, Periodicity[periodicity.upper()], task_template).save()
