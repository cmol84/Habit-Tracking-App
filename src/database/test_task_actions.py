from .test_habit_actions import generate_test_data
import pytest
from .db import Periodicity


@pytest.mark.parametrize("habits", generate_test_data())
def test_task_creation(db_connection, habits):
    for row in habits:
        db_connection.create_habit(row[0], row[1], row[2])

    for habit in db_connection.select_habits('*'):
        db_connection.create_task_from_habit(habit)
        tasks = db_connection.select_tasks(id_habit=habit.get('id_habit'))
        assert len(tasks) == len(habit.get('template'))
        task_name = [t.get('task') for t in tasks]
        for template_task in habit.get('template'):
            assert template_task in task_name


def test_delete_task_overdue(db_connection):
    habit = db_connection.create_habit(
        'Habit 1 overdue',
        Periodicity.DAILY,
        ['Task 1 Overdue', 'Task 2 Overdue', 'Task 3 Overdue']
    )
    # We should get back a result because we have no tasks created yet, therefore it should be
    # returned.
    assert len(db_connection.sync_states()) == 1
    db_connection.create_task_from_habit(habit)
    # We now have tasks on an active habit so nothing should be returned
    assert len(db_connection.sync_states()) == 0

    db_connection.cursor.execute(
        "UPDATE habits set updated_at = datetime('now', '-5 DAY', 'LOCALTIME') "
        'where id_habit = ?', [habit.get('id_habit')]
    )
    db_connection.connection.commit()
    # We updated the updated_at date, and now we need to return something on an overdue habit
    assert len(db_connection.sync_states()) == 1
