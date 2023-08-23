"""
This module contains test cases for the task-related functionalities of the application.

It utilizes the pytest framework for testing and relies on the `database` module
for interacting with the application's database. The test cases in this module ensure
the proper creation and deletion of tasks associated with habits, as well as handling
overdue tasks.

Module Dependencies:
    - pytest
    - database.Periodicity
    - database.Habit
    - database.Task
    - .test_habit_actions.generate_test_data

Test Functions:

    - test_task_creation(db_connection, habits)

      This function tests the creation of tasks based on habits and ensures that
      the generated tasks match the expected template tasks.

    - test_delete_task_overdue(db_connection)

      This function tests the deletion of overdue tasks from a habit, simulating
      the behavior when tasks become overdue.

"""
from datetime import timedelta

import pytest

from database import Periodicity, Habit, Task
from .test_habit_actions import generate_test_data


@pytest.mark.parametrize("habits", generate_test_data())
def test_task_creation(db_connection, habits):
    """
    Test the creation of tasks from habits.

    This test function verifies the creation of tasks from habits by iterating through the provided
    list of habits, creating corresponding tasks for each habit, and then comparing the generated
    tasks with the expected template tasks.

    Args:
        db_connection (DatabaseConnection): The database connection object.
        habits (List[Tuple]): A list of tuples representing habits' data, each containing habit
                              attributes (name, description, template).

    Raises:
        AssertionError: If the number of generated tasks does not match the number of expected
                        template tasks for a habit, or if the generated task names do not match
                        the template task names.
        """

    for row in habits:
        Habit(row[0], row[1], row[2], db=db_connection).save()

    for habit in list(Habit.objects(db=db_connection)):
        Task.from_habit(habit, db=db_connection)
        tasks = list(Task.objects(habit, db=db_connection))
        assert len(tasks) == len(habit.template)
        task_name = [t.task for t in tasks]
        for template_task in habit.template:
            assert template_task in task_name


def test_delete_task_overdue(db_connection):
    """
    Test the behavior of deleting tasks from an overdue habit.

    This method creates an overdue habit with tasks, manipulates the habit's last update
    timestamp, and then checks the behavior of task deletion on overdue habits using
    the provided database connection.

    Args:
        db_connection (DatabaseConnection): The database connection object.

    Returns:
        None

    Raises:
        AssertionError: If any of the test conditions fail.
    """

    habit = Habit(
        'Habit 1 overdue',
        Periodicity.DAILY,
        ['Task 1 Overdue', 'Task 2 Overdue', 'Task 3 Overdue'],
        db=db_connection
    ).save()
    # We should get back a result because we have no tasks created yet, therefore it should be
    # returned.
    assert len(list(Habit.objects(finished=True, db=db_connection))) == 1
    Task.from_habit(habit, db=db_connection)
    # We now have tasks on an active habit so nothing should be returned
    assert len(list(Habit.objects(finished=True, db=db_connection))) == 0
    assert len(list(Task.objects(db=db_connection))) == 3
    # Here we expire the habit for the next test
    habit.updated_at = habit.updated_at - timedelta(days=5)
    habit.save()

    # We updated the updated_at date, and now we need to return something on an overdue habit
    assert len(list(Habit.objects(finished=True, db=db_connection))) == 1
