import pytest
import functools as func
from database import Habit, Task, Report, Periodicity


def test_report_generation(db_connection):
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
