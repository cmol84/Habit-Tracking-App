"""
This command generates a list of habits with their main attributes.
"""

import click
from tabulate import tabulate
from database.db import DB, as_array
from cli import cli

db = DB()


@cli.command()
def list_habits():
    """
    This creates a list of habits currently available.

    This code defines a function called list_habits that retrieves a list of
    habits from a database and displays them in a formatted table using the
    tabulate library.

    The function uses the db.select_habits method to retrieve the habits from
    the database, and the as_array parameter is used to return the results as
    a list of arrays instead of a list of dictionaries.

    The tabulate function is then used to format the table with a fancy outline
    style, and the headers for the table are specified as well.
    The resulting table is printed to the console.
    """
    table = db.select_habits(row_factory=as_array)
    print(tabulate(
        table,
        tablefmt="fancy_outline",
        headers=["ID", "Name", "Periodicity", "Streak", "Tasks", "Completed"]
    ))
