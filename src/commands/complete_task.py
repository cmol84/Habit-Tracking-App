"""
This command allows users to select the tasks from a list of habits and tasks and mark it as
completed, either by providing task ids one by one or a list of multiple tasks.
"""

import click

from cli import cli
from database import Task


@cli.command()
def complete_task():
    """
    Mark tasks as completed.

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
    last_habit = None
    for task in Task.objects():
        print(task.habit())
        habit_name = task.habit().name
        if last_habit != habit_name:
            print(habit_name)
        checked = 'x' if task.completed else ' '
        print(f"- [{checked}] [{task.id_task}] {task.task}")
        last_habit = habit_name
    while True:
        id_task = click.prompt('Please provide the task ID you want to mark as completed', type=int)
        if id_task:
            task = Task.get(id_task)
            task.completed = True
            task.save()
        if not click.confirm('Do you want to select another one?'):
            break
