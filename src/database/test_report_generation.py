"""
This module provides a function for testing the report generation process.

It contains the following function:
  - test_report_generation(db_connection):

    This function tests the report generation
    process by creating a Habit, associated Tasks, generating reports, and verifying the
    outcomes. It takes a database connection as a parameter.

Usage:
  from database import Habit, Task, Report, Periodicity
  from this_module import test_report_generation
  db_connection = ...  # create a database connection
  test_report_generation(db_connection)
"""

from database import Habit, Task, Report, Periodicity


def test_report_generation(db_connection):
    """
    Test the report generation process for a Habit instance.

    This method performs a series of actions to test the generation of reports
    for a Habit instance and its associated tasks. It checks the behavior of
    generating reports, updating task completions, and verifying streak counts.

    Args:
        db_connection (DatabaseConnection): A connection to the database.

    Raises:
        AssertionError: Raised if any of the test assertions fail.
    """

    habit = Habit(
        'Habit 1 overdue',
        Periodicity.DAILY,
        ['Task 1 Overdue', 'Task 2 Overdue', 'Task 3 Overdue'],
        db=db_connection,
    ).save()
    Task.from_habit(habit, db=db_connection)
    db_connection.cursor.execute(
        "UPDATE tasks set completed = TRUE where id_habit = ?",
        [habit.id_habit]
    )
    db_connection.connection.commit()

    query_rep = db_connection.cursor.execute(
        "SELECT * from reports WHERE id_habit = ?",
        [habit.id_habit]
    )

    assert len(query_rep.fetchall()) == 0
    Report(habit.id_habit, db=db_connection).generate()
    query_rep = db_connection.cursor.execute(
        "SELECT * from reports WHERE id_habit = ?",
        [habit.id_habit]
    )
    assert len(query_rep.fetchall()) == 1
    assert len(list(Task.objects(habit, db=db_connection))) == 0
    updated_habit = Habit.get(habit.id_habit, db=db_connection)
    assert updated_habit.streak == 1

    Task.from_habit(habit, db=db_connection)

    Report(habit.id_habit, db=db_connection).generate()
    query_rep = db_connection.cursor.execute(
        "SELECT * from reports WHERE id_habit = ?",
        [habit.id_habit]
    )

    assert len(query_rep.fetchall()) == 2
    updated_habit = Habit.get(habit.id_habit, db=db_connection)
    assert updated_habit.streak == 0
