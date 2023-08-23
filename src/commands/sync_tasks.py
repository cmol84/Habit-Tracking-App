"""
This command syncs the states of the tasks belonging to different habits. It is also
enabled to automatically generate reports entries, based on different conditions, data that will
be later on queried to generate the visualised reports. It will also generate the tasks from the
templates provided in the habit creation so that you can follow up on the progress.
"""

from cli import cli
from database import Task, Habit, Report


@cli.command()
def sync_tasks():
    """
    Generate tasks and fill in report data automatically.

    This code defines a command-line interface (CLI) command called `sync_tasks`.
    When this command is executed, it performs the following actions:
    1. It loops through all the habits in the database and checks if any of them
    have tasks that need to be completed. If a habit has incomplete tasks,
    it generates a report for that habit using the `generate_report` function.

    2. It then loops through all the habits in the database and creates new tasks
    for any habit that needs to be fulfilled. It does this by looping through the
    habit's task template and creating a new task for each task in the template
    using the `create_task` function.

    Overall, this command is intended to synchronize the tasks for all habits in
    the database with the tasks defined in the habit templates.
    It also generates reports for any incomplete habits and creates new tasks
    for any habit that needs to be fulfilled.
    """
    for habit in Habit.objects(finished=True):
        Report(habit.id_habit).generate()

    for habit in Habit.objects(no_tasks=True):
        Task.from_habit(habit)
