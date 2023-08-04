from test_habit_actions import generate_test_data


@pytest.mark.parametrize("habits", generate_test_data())
def test_task_creation(db_connection, habits):
    inserted_tasks = []
    for row in habits:
        db_connection.create_habit(row[0], row[1], row[2])

