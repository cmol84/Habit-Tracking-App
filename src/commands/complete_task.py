"""
This command allows users to select the tasks from a list of habits and tasks and mark it as
completed, either by providing task ids one by one or a list of multiple tasks.
"""

import click
from database.db import DB
from cli import cli

db = DB()


@cli.command()
def complete_task():
    """
    This is where users can mark tasks as done.

    This code defines a command-line interface (CLI) command called `complete_task`.
    When this command is executed, it first displays a list of all tasks in the database,
    with each task displayed as a bullet point with a checkbox next to it if the
    task has been completed and a hyphen if it has not been completed.

    The user is then prompted to enter the ID of the task they want to mark as completed.
    If the user enters a valid task ID, the `update_completed` function in the
    database module is called to update the completed status of the task in the database.

    The user is then prompted to mark another task as completed, and the process
    repeats until they choose not to.
    """
    table = db.select_tasks()
    last_habit = None
    for row in table:
        habit_name = row.get('name')
        if last_habit != habit_name:
            print(habit_name)
        checked = 'x' if row.get('completed') else ' '
        print(f"- [{checked}] [{row.get('id_task')}] {row.get('task')}")
        last_habit = habit_name
    while True:
        id_task = click.prompt('Please provide the task ID you want to mark as completed', type=int)
        if id_task:
            db.update_completed(id_task)
        if not click.confirm('Do you want to select another one?'):
            break
