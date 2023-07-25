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
    for habit in db.select_executable_habits():
        # TODO: Move this into its own function
        if habit.get('task_count') == 0:
            for task in habit.get('template'):
                db.create_task(habit.get('id_habit'), task)

    # TODO: select all the tasks that are either over the periodicity or the tasks are completed
    #  and when true create a report that says habit achieved and streak updated
    # TODO: delete outdated or completed tasks either from task or habit perspective
    # TODO: insert data into reports before deleting the data


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
        click.confirm(f'Are you sure you want to delete the Habit with ID: {id_habit}? '
                      f'Please note that this will recursively delete all tasks belonging to '
                      f'the provided habit!')
        if not click.confirm('Do you want to delete another one?'):
            break
    db.delete_habit(id_habit)


@cli.command()
def complete_task():
    table = db.select_tasks()
    last_habit = None
    for row in table:
        habit_name = row.get('name')
        if last_habit != habit_name:
            print(habit_name)
        print(f"[ ] {row.get('id_task'), row.get('task')}")
        last_habit = habit_name
    while True:
        id_task = click.prompt(
            'Please provide the task ID you want to mark as completed', type=int)
        if not click.confirm('Do you want to select another one?'):
            break
    db.update_completed(id_task)


# TODO: add checkbox and set an X if completed == true


@cli.command()
def analyse_data():
    pass


if __name__ == "__main__":
    # Greeting message
    print("""
    *** Welcome to My Habit Tracker ***
    """)
    from database.db import DB

    db = DB()
    cli()
