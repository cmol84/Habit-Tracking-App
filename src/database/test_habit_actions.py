"""
Module Docstring:

This module contains test cases for inserting and managing habits in a database.

It defines the following functions and test cases:

- test_daily_habit_actions(db_connection, name: str, periodicity: Periodicity):
  This test ensures that habits with all options for periodicity are inserted and #subsequently
  removed from the database.

- generate_test_data():
  Generates test data for habit insertion testing. This includes habits with tasks
  and habits without tasks.

- test_list_habits(db_connection, habits):
  Tests the listing of inserted habits. It inserts habits into the database, retrieves
  them, and compares the results from the API and the database.

Note: This module is designed for testing purposes and contains test cases related to
habit management.
"""

import random

import pytest
from faker import Faker

from database import Periodicity
from .habit import Habit

fake = Faker()
Faker.seed(1)

testdata = [
    ('name', Periodicity.DAILY),
    ('name', Periodicity.WEEKLY),
    ('name', Periodicity.MONTHLY),
]

"""This test ensures that habits with all options for periodicity are inserted and subsequently 
removed from the database"""


@pytest.mark.parametrize("name,periodicity", testdata)
def test_daily_habit_actions(db_connection, name: str, periodicity: Periodicity):
    """
       Test the actions related to daily habits.

       This test function creates a new habit, inserts it into the database,
       and then performs several checks to ensure the correctness of the insertion
       and deletion processes.


       Args:

           db_connection (DBConnection): An instance of the database connection.
           name (str): The name of the habit.
           periodicity (Periodicity): The periodicity of the habit.


       Steps:

        1. Create a new habit instance and save it to the database.
        2. Retrieve all records from the 'habits' table.
        3. Check that the number of records is greater than 0.
        4. Retrieve the first row's data and compare 'name' and 'periodicity' values.
        5. Check that there is only 1 record in the result.
        6. Delete the habit instance.
        7. Retrieve records again and ensure that no records exist.

       Raises:
           AssertionError: If any of the checks fail during the test execution.
       """
    # create new habit and check it's inserted correctly
    # db_connection.create_habit(name, periodicity, [])
    habit_instance = Habit(name, periodicity, [], db=db_connection).save()
    statement = db_connection.cursor.execute('''SELECT * FROM habits;''')
    result = statement.fetchall()

    assert len(result) > 0
    row: dict = result[0]
    assert row["name"] == name
    assert row["periodicity"] == periodicity.value

    # check that there is 1 record
    assert len(result) == 1
    # delete record
    habit_instance.delete()
    result = statement.fetchall()
    assert len(result) == 0


def generate_test_data():
    """
       Generate test data for habits, including names, periodicity, and task lists.

       This function generates two lists: one containing habits with associated task lists,
       and another containing habits without any tasks.

       Returns:
           list: A list containing two sublists:
               - `testdata_list_habits` (list): A list of habits with associated details.
                 Each habit is represented as a sublist containing:
                   - name (str): The name of the habit.
                   - periodicity (Periodicity): The periodicity of the habit
                     (daily, weekly, monthly).
                   - task_list (list): A list of tasks associated with the habit.
               - `habits_without_tasks` (list): A list of habits without any associated tasks.
                 Each habit is represented as a sublist containing:
                   - name (str): The name of the habit.
                   - periodicity (Periodicity): The periodicity of the habit
                     (daily, weekly, monthly).
                   - task_list (list): An empty list since there are no tasks associated.
       """
    testdata_list_habits = []
    for _ in range(10):
        name = fake.word()
        periods = ([Periodicity.DAILY, Periodicity.WEEKLY, Periodicity.MONTHLY])
        periodicity = random.choice(periods)
        task_list = fake.texts(nb_texts=5, max_nb_chars=40)
        testdata_list_habits.append([
            name,
            periodicity,
            task_list
        ])

    habits_without_tasks = []
    for _ in range(10):
        name = fake.word()
        periods = ([Periodicity.DAILY, Periodicity.WEEKLY, Periodicity.MONTHLY])
        periodicity = random.choice(periods)
        task_list = []
        habits_without_tasks.append([
            name,
            periodicity,
            task_list
        ])

    return [testdata_list_habits, habits_without_tasks]


@pytest.mark.parametrize("habits", generate_test_data())
def test_list_habits(db_connection, habits):
    """
    Test the behavior of listing habits using the provided database connection.

    This test function uses parameterized testing with various sets of habits
    generated by the 'generate_test_data' function.

    Args:
        db_connection (connection): A database connection object.

    """
    inserted_names = []
    for row in habits:
        Habit(row[0], row[1], row[2], db=db_connection).save()
        inserted_names.append(row[0])

    query = db_connection.cursor.execute('''SELECT * FROM habits;''')
    db_result = query.fetchall()
    api_result = list(Habit.objects(db=db_connection))

    assert len(habits) == len(db_result)
    assert len(api_result) == len(db_result)

    api_names = []
    for item in api_result:
        api_names.append(item.name)

    for row in db_result:
        assert row.get('name') in inserted_names
        assert row.get('name') in api_names
        habit_index = inserted_names.index(row.get('name'))
        habit_tasks = habits[habit_index][2]
        for task in habit_tasks:
            assert task in row.get('template')
