from database.db import Periodicity
import pytest
from faker import Faker
from typing import List, Tuple
import random

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
    db_connection.create_habit(name, periodicity, [])
    statement = db_connection.cursor.execute("""SELECT * FROM habits;""")
    result = statement.fetchall()

    row: dict = result[0]
    assert row["name"] == name
    assert row["periodicity"] == periodicity.value

    # check that there is 1 record
    assert len(result) == 1
    # delete record
    db_connection.delete_habit(row.get('id_habit'))
    # check db to be empty

    result = statement.fetchall()
    assert len(result) == 0


def generate_test_data() -> List[List[Tuple[str, Periodicity, List[str]]]]:
    # iterate through a random amount - done
    # generate names, periodicity and list of tasks - done
    testdata_list_habits = []
    for _ in range(5):
        name = fake.word()
        periods = (["Daily", "Weekly", "Monthly"])
        periodicity = random.choice(periods)
        task_list = fake.texts(nb_texts=5, max_nb_chars=40)
        testdata_list_habits.append([
            name,
            periodicity,
            task_list
        ])

    return testdata_list_habits


@pytest.mark.parametrize("habits", generate_test_data())
def test_list_habits(db_connection, habits):
    statement = "INSERT INTO `habits`(`name`, `periodicity`, `template`)" \
                "VALUES (%s, %s, %s);"

    # iterate through the habits & insert with sql statements
    # OR use the create habit method
    # -> EASY WAY: db_connection.create_habit(name, periodicity, [])

    query = db_connection.cursor.execute("""SELECT * FROM habits;""")
    result = query.fetchall()
    # compare result with habits and see if all the names exist in result.
    # optional check the order of the names -> HINT: for loop from habits
