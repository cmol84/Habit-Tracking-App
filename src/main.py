"""
Here we want to register the commands for the click app, serve the basic version and help
commands and execute the click app from the CLI arguments.
"""
from database.db import DB, Periodicity, as_array, as_dictionary
import click
from tabulate import tabulate

db = DB()


@click.group()
# @click.option('--version')
def cli():
    pass


@cli.command()
def list_habits():
    table = db.select_habits(row_factory=as_array)
    print(tabulate(
        table,
        tablefmt="fancy_outline",
        headers=["ID", "Name", "Periodicity", "Streak", "Tasks", "Completed"]
    ))


@cli.command()
def create_habit():
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
        if not click.confirm('Do you want to continue?'):
            break
    db.create_habit(name, Periodicity[periodicity.upper()], task_template)


@cli.command()
def sync_tasks():
    for habit in db.check_task_status():
        task_list = db.select_tasks(habit.get('id_habit'))
        db.generate_report(habit, task_list)

    for habit in db.select_habits_to_fulfill():
        # TODO: Move this into its own function
        for task in habit.get('template'):
            db.create_task(habit.get('id_habit'), task)


@cli.command()
def delete_habit():
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


@cli.command()
def complete_task():
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


@cli.command()
def analyse_data():
    table = [
        ['1', 'List all habits'],
        ['2', 'List all habits with the same periodicity'],
        ['3', 'Longest run streak of all defined habits'],
        ['4', 'Shortest run streak of all defined habits'],
        ['5', 'Longest run streak for a given habit'],
    ]
    print(tabulate(
        table,
        tablefmt="fancy_outline",
        headers=["Report ID", "Report Name"]))
    match click.prompt('Please provide the Report ID of the report you want execute', type=int):
        case 1:
            table = db.select_habits(row_factory=as_array)
            print(tabulate(
                table,
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
            table = db.report_longest_streak(row_factory=as_array)

            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit Name", "Streak"]))

        case 4:
            table = db.report_shortest_streak(row_factory=as_array)

            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit Name", "Streak"]))

        case 5:
            table = db.get_habit_list_snapshot(row_factory=as_array)
            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit ID", "Habit Name"]))

            id_habit = click.prompt(
                'Please provide the Habit ID for which you want execute the report', type=int)

            table = db.report_longest_streak_given_habit(id_habit, row_factory=as_array)

            print(tabulate(
                table,
                tablefmt="fancy_outline",
                headers=["Habit Name", "Streak"]))


if __name__ == "__main__":
    # Greeting message
    print("""
    *** Welcome to My Habit Tracker ***
    """)
    from database.db import DB

    db = DB()
    cli()
