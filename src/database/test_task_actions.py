from .test_habit_actions import generate_test_data
import pytest
from database import Periodicity, Habit, Task


@pytest.mark.parametrize("habits", generate_test_data())
def test_task_creation(db_connection, habits):
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
    habit = Habit(
        'Habit 1 overdue',
        Periodicity.DAILY,
        ['Task 1 Overdue', 'Task 2 Overdue', 'Task 3 Overdue'],
        db=db_connection
    ).save()
    # We should get back a result because we have no tasks created yet, therefore it should be
    # returned.
    assert len(db_connection.sync_states()) == 1
    Task.from_habit(habit, db=db_connection)
    # We now have tasks on an active habit so nothing should be returned
    assert len(db_connection.sync_states()) == 0
    assert len(list(Task.objects(db=db_connection))) == 3

    db_connection.cursor.execute(
        "UPDATE habits set updated_at = datetime('now', '-5 DAY', 'LOCALTIME') "
        'where id_habit = ?', [habit.id_habit]
    )
    db_connection.connection.commit()
    # We updated the updated_at date, and now we need to return something on an overdue habit
    assert len(db_connection.sync_states()) == 1
