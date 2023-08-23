import json
from dataclasses import dataclass
from datetime import datetime
from typing import Generator

from .db import DB, DATE_FORMAT
from .habit import Habit
from .task import Task


@dataclass
class Report:
    """
    A class representing a report containing information about habits and tasks.

    Attributes:
        id_habit (int): The ID of the associated habit.
        id_report (int, optional): The ID of the report (default is None).
        name (str, optional): The name of the report (default is None).
        current_streak (int, optional): The current streak of the habit (default is None).
        completed_tasks_count (int, optional): The count of completed tasks (default is None).
        uncompleted_tasks_count (int, optional): The count of uncompleted tasks (default is None).
        created_at (datetime, optional): The timestamp when the report was created (default
          is the current datetime).
        raw_data (dict, optional): Raw data associated with the report (default is None).
        db (DB, optional): An instance of the DB class for database operations (default
          is an instance of DB).

    Note:
        The `DB` class should be imported and provided to the `db`
          attribute for database operations.
        """
    id_habit: int
    id_report: int = None
    name: str = None
    current_streak: int = None
    completed_tasks_count: int = None
    uncompleted_tasks_count: int = None
    created_at: datetime = datetime.now()
    raw_data: dict = None
    db: DB = DB()

    @staticmethod
    def _map_report(row, db: DB = DB()):
        return Report(
            id_report=row.get('id_report'),
            id_habit=row.get('id_habit'),
            name=row.get('name'),
            current_streak=row.get('current_streak'),
            completed_tasks_count=row.get('completed_tasks_count'),
            uncompleted_tasks_count=row.get('uncompleted_tasks_count'),
            created_at=datetime.strptime(row.get('created_at'), DATE_FORMAT),
            db=db
        )

    @staticmethod
    def objects(db: DB = DB()) -> Generator:
        query = db.cursor.execute('SELECT * FROM reports')
        for row in query.fetchall():
            yield Report._map_report(row, db=db)

    def save(self):
        """
        Saves the current state of the habit report into the database.

        This method computes statistics about the associated Habit and its Task objects,
        and inserts a new entry into the 'reports' table in the database to store the
        report data. It also updates the `id_report` attribute of the instance based on
        the newly generated report.

        Returns:
            int: The ID of the generated report.

        Raises:
            DatabaseError: If there's an issue with the database operations.

        Note:
            This method assumes that the `Habit` and `Task` classes are properly defined
            and that the database connection and cursor are available through `self.db`.

        """
        habit = Habit.get(self.id_habit, db=self.db)
        task_list = list(Task.objects(habit, db=self.db))

        uncompleted_tasks_count = len(task_list)
        completed_tasks_count = 0
        for task in task_list:
            uncompleted_tasks_count -= 1 if task.completed else 0
            completed_tasks_count += 1 if task.completed else 0

        self.db.cursor.execute(
            '''INSERT INTO reports (id_habit, name, current_streak, completed_tasks_count, 
                        uncompleted_tasks_count, raw_data, id_report, created_at) VALUES (?, ?, ?, 
                        ?, ?, ?, ? , ?)''',
            (
                habit.id_habit,
                habit.name,
                habit.streak,
                completed_tasks_count,
                uncompleted_tasks_count,
                json.dumps([task.to_json() for task in task_list]),
                self.id_report,
                self.created_at.strftime(DATE_FORMAT)
            ),
        )
        self.db.connection.commit()
        query = self.db.cursor.execute(
            '''SELECT * FROM reports 
            where id_habit = ? 
            and created_at = (select MAX(created_at) from reports)''',
            [self.id_habit])
        raw_data = query.fetchone()
        self.id_report = raw_data.get('id_report')
        return self

    def generate(self):
        """
        Generates a new habit progress report, updating the habit's streak and completing tasks.

        This method generates a progress report for the habit, including updating the habit's streak
        based on completed tasks. It also deletes all tasks associated with the habit and completes
        them in the process.

        Steps:
          1. Save the current state of the habit.
          2. Retrieve the habit from the database using the provided habit ID.
          3. Retrieve a list of tasks associated with the habit.
          4. Delete all tasks associated with the habit.
          5. Calculate the number of completed tasks.
          6. Update the habit's streak based on completed tasks.
          7. Save the updated habit to the database.

        Note:

        - The habit's streak is incremented if all tasks are completed, otherwise, it's reset to 0.
        - This method assumes the existence of the Habit and Task classes, and
        a database connection.

        Returns:
            None
        """
        self.save()

        habit = Habit.get(self.id_habit, db=self.db)
        task_list = list(Task.objects(habit, db=self.db))
        for task in task_list:
            task.delete()

        done_tasks = 0
        for task in task_list:
            done_tasks += 1 if task.completed else 0
        habit.streak = habit.streak + 1 if done_tasks == len(task_list) else 0
        habit.save()

    def delete(self):
        if self.id_report is None:
            raise ReferenceError(
                'This instance has not been saved yet so you cannot delete it!')
        self.db.cursor.execute(
            '''DELETE FROM reports WHERE id_report = ?''',
            [self.id_report]
        )
        self.db.connection.commit()
        return self
