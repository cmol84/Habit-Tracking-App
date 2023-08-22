from database.db import Periodicity, DB
from __test__ import db_connection
import pytest
from faker import Faker
from typing import List, Tuple
import random
import json
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
    # iterate through a random amount - done
    # generate names, periodicity and list of tasks - done
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
    inserted_names = []
    for row in habits:
        Habit(row[0], row[1], row[2], db=db_connection).save()
        inserted_names.append(row[0])

    query = db_connection.cursor.execute('''SELECT * FROM habits;''')
    db_result = query.fetchall()
    api_result = list(Habit.objects(db_connection))

    assert len(habits) == len(db_result)
    assert len(api_result) == len(db_result)

    api_names = []
    for item in api_result:
        api_names.append(item.name)

    for index, row in enumerate(db_result):
        assert row.get('name') in inserted_names
        assert row.get('name') in api_names
        habit_index = inserted_names.index(row.get('name'))
        habit_tasks = habits[habit_index][2]
        for task in habit_tasks:
            assert task in row.get('template')
