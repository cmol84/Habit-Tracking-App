import pytest
from .db import Periodicity


def test_report_generation(db_connection):
    habit = db_connection.create_habit(
        'Habit 1 overdue',
        Periodicity.DAILY,
        ['Task 1 Overdue', 'Task 2 Overdue', 'Task 3 Overdue'],
    )
    db_connection.create_task_from_habit(habit)

    db_connection.cursor.execute(
        "UPDATE tasks set completed = TRUE where id_habit = ?",
        [habit.get('id_habit')]
    )
    db_connection.connection.commit()
    # we simulate the special query from db.py
    habit['completed_tasks_count'] = 3
    habit['uncompleted_tasks_count'] = 0
    habit['current_streak'] = habit.get('streak')

    task_list = db_connection.select_tasks(habit.get('id_habit'))

    query_rep = db_connection.cursor.execute(
        "SELECT * from reports WHERE id_habit = ?",
        [habit.get('id_habit')]
    )

    assert len(query_rep.fetchall()) == 0
    db_connection.generate_report(habit, task_list)
    query_rep = db_connection.cursor.execute(
        "SELECT * from reports WHERE id_habit = ?",
        [habit.get('id_habit')]
    )
    assert len(query_rep.fetchall()) == 1
    assert len(db_connection.select_tasks(habit.get('id_habit'))) == 0
    updated_habit = db_connection.select_habits('*', habit.get('id_habit'))
    assert updated_habit[0].get('streak') == 1

    db_connection.create_task_from_habit(habit)
    habit['completed_tasks_count'] = 0
    habit['uncompleted_tasks_count'] = 3
    habit['current_streak'] = habit.get('streak')
    db_connection.generate_report(habit, task_list)
    query_rep = db_connection.cursor.execute(
        "SELECT * from reports WHERE id_habit = ?",
        [habit.get('id_habit')]
    )
    assert len(query_rep.fetchall()) == 2
    updated_habit = db_connection.select_habits('*', habit.get('id_habit'))
    assert updated_habit[0].get('streak') == 0
