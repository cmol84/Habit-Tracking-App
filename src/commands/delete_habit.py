"""
This command allows users to ge ta list of existing habits and then provide the id of the
habit to be deleted.
As soon as that is provided and action confirmed, the habit and all of its tasks are deleted.
"""
import click
from tabulate import tabulate
from database.db import DB, as_array
from cli import cli

db = DB()


@cli.command()
def delete_habit():
    """
    Delete existing habits.

    This code defines a command-line interface (CLI) command called `delete_habit`.
    When this command is executed, it first displays a list of all currently active
    habits using the `select_habits` function from the `db` module. The list is
    formatted using the `tabulate` function and displayed in a fancy outline format.

    The user is then prompted to enter the ID of the habit they want to delete.
    If the user confirms that they want to delete the habit, the `delete_habit`
    function from the `db` module is called with the provided ID.
    If the user confirms that they want to delete another habit, the process starts over.

    The `delete_habit` function recursively deletes all tasks belonging to the
    provided habit, and then deletes the habit itself.
    """
    print("Here is the list of currently active habits:")
    table = db.select_habits(row_factory=as_array)
    print(tabulate(
        table,
        tablefmt="fancy_outline",
        headers=["ID", "Name", "Periodicity", "Streak", "Tasks", "Completed"]
    ))
    while True:
        id_habit = click.prompt('Please type the ID of the habit you want to delete', type=int)
        if click.confirm(
                f'Are you sure you want to delete the Habit with ID: {id_habit}? '
                f'Please note that this will recursively delete all tasks belonging to '
                f'the provided habit!'):
            db.delete_habit(id_habit)
        if not click.confirm('Do you want to delete another one?'):
            break
