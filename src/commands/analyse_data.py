"""
This command executes all the predefined reports users can access.
"""

import click
from tabulate import tabulate

from cli import cli
from database import DB, Periodicity, as_array, Habit

db = DB()


@cli.command()
def analyse_data():
    """
    Generate and display reports.

    The `analyse_data()` function displays a list of available reports and prompts the user
    to select a report to execute. It then uses the appropriate methods of the `db` object to
    retrieve and format the data for the selected report, using the `tabulate()` function from
    the `tabulate` library. The available reports include listing all habits, listing habits
    with the same periodicity, finding the longest and shortest run streaks for all habits,
    finding the longest run streak for a given habit, and getting a snapshot of the habit list.
    """
    table = [
        ['1', 'Your current streak overview'],
        ['2', 'List all habits with the same periodicity'],
        ['3', 'Longest run streak for a given habit'],
        ['4', 'Longest run streak of all defined habits'],
        ['5', 'Shortest run streak of all defined habits'],
    ]
    print(tabulate(
        table,
        tablefmt="fancy_outline",
        headers=["Report ID", "Report Name"]))
    match click.prompt('Please provide the Report ID of the report you want to execute', type=int):
        case 1:
            print(tabulate(
                [h.as_tabulate() for h in Habit.objects()],
                tablefmt="fancy_outline",
                headers=["ID", "Name", "Periodicity", "Streak", "Tasks", "Completed"]
            ))

        case 2:
            periodicity_options = [
                v.name for v in list(Periodicity)
            ]
            periodicity = click.prompt(
                'Please enter the habit Periodicity',
                type=click.Choice(periodicity_options, case_sensitive=False)
            )
            table = db.report_same_period(periodicity, row_factory=as_array)

            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Periodicity", "Habit Name"]))

        case 3:

            table = db.get_habit_list_snapshot(row_factory=as_array)
            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit ID", "Habit Name"]))

            id_habit = click.prompt(
                'Please provide the Habit ID for which you want to execute the report', type=int)

            table = db.report_longest_streak_given_habit(id_habit, row_factory=as_array)

            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit Name", "Streak"]))

        case 4:

            table = db.report_longest_streak(row_factory=as_array)

            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit Name", "Streak"]))

        case 5:

            table = db.report_shortest_streak(row_factory=as_array)

            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit Name", "Streak"]))
