"""
The database module: Primarily creates database tables, stores information and returns data.
"""
import json
import sqlite3
from pathlib import Path
from .types import Periodicity

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DB_PATH = Path(__file__).parent.parent.parent.resolve()


def as_dictionary(cursor, row):
    """
    Converts a database row into a dictionary.

    Args:
        * cursor (sqlite3.Cursor): The database cursor object.
        * row (tuple): The values of a database row.
    Returns: dict: A dictionary mapping column names to row values."""

    fields = [column[0] for column in cursor.description]
    data = dict(zip(fields, row))
    if 'template' in data:
        data['template'] = json.loads(data.get('template'))
    return data


def as_array(_cursor, row):
    """ A simple function that returns the input row as-is.

    Args:
        * _cursor: Placeholder argument (not used).
        * row (tuple): The values of a database row.
    Returns: tuple: The input row."""

    return row


class DB:
    """ Represents a database module that handles habit tracking data.

    Attributes:
        * connection (sqlite3.Connection): The SQLite database connection.
        * cursor (sqlite3.Cursor): The database cursor object."""

    def __init__(self, name="habit_tracking_app.db"):
        """ Creates a database connection and sets the row factory.
        Args:
            name (str, optional): The name of the database to create or connect with.
            Defaults to "habit_tracking_app.db"."""

        self.connection = sqlite3.connect(f'{DB_PATH}/{name}')
        self._set_row_factory()
        self._migrate()

    def _migrate(self):
        """ Migrates the database schema to create required tables.

        The 'habits' table consists of the following columns:
            - id_habit (int): Primary key representing habit ID.
            - name (str): Name of the habit.
            - periodicity (str): Periodicity of the habit.
            - streak (int): Habit's current streak count.
            - template (str): JSON string representing the habit template.
            - created_at (timestamp): Date and time of habit creation.
            - updated_at (timestamp): Date and time of last habit update.

        The 'tasks' table contains the following columns:
            - id_task (int): Primary key representing task ID.
            - id_habit (int): Foreign key referencing the habit.
            - task (str): Text representing the task.
            - completed (bool): Flag indicating task completion.
            - created_at (timestamp): Date and time of task creation.
            - updated_at (timestamp): Date and time of last task update.

        The 'reports' table will contain the following columns:
            - id_report (int): Primary key representing report ID.
            - id_habit (int): Foreign key referencing the habit.
            - name (str): Name of the habit.
            - current_streak (int): Habit's current streak count.
            - completed_tasks_count (str): JSON string representing completed task count.
            - uncompleted_tasks_count (str): JSON string representing uncompleted task count.
            - created_at (timestamp): Date and time of report creation.
            - raw_data (str): JSON string representing the list of task dictionaries."""

        self.cursor.execute('''PRAGMA foreign_keys = ON;''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id_habit INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL UNIQUE, 
                periodicity TEXT, 
                streak INT DEFAULT 0,
                template TEXT NOT NULL, 
                created_at timestamp DATE DEFAULT (datetime('now','localtime')), 
                updated_at timestamp DATE DEFAULT (datetime('now','localtime'))
           )''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id_task INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_habit INTEGER NOT NULL, 
                task NOT NULL,
                completed BOOL NOT NULL DEFAULT FALSE,
                created_at timestamp DATE DEFAULT (datetime('now','localtime')), 
                updated_at timestamp DATE DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (id_habit) REFERENCES habits(id_habit)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id_report INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_habit INTEGER NOT NULL, 
                name VARCHAR(255) NOT NULL,
                current_streak INT,
                completed_tasks_count TEXT NOT NULL,
                uncompleted_tasks_count TEXT NOT NULL,
                created_at timestamp DATE DEFAULT (datetime('now','localtime')),
                raw_data TEXT NOT NULL, --list of dicts of tasks
                FOREIGN KEY (id_habit) REFERENCES habits(id_habit)
            )
        ''')
        self.connection.commit()

    def _set_row_factory(self, row_factory=as_dictionary):
        """ Sets the row factory for the database connection.

        Args:
            row_factory (function, optional): The function to use as the row factory.
            Defaults to `as_dictionary`."""

        self.connection.row_factory = row_factory
        self.cursor = self.connection.cursor()

    def report_same_period(self, periodicity: str, row_factory=as_dictionary):
        """
            Report that returns a list of all habits with the same periodicity.

            Args:
                periodicity (str): A string that specifies the periodicity of the
                    habits to be returned in the report.
                row_factory (function, optional):
                    A function that specifies how the rows returned by the database query
                    should be represented.

                    The default value is `as_dictionary`, which returns
                    the rows as dictionaries where the keys are the column names and the values
                    are the column values.

            Returns:
                list: A list of dictionaries, where each dictionary represents a row and
                the keys are the column names and the values are the column values. """
        self._set_row_factory(row_factory)
        query = self.cursor.execute(
            '''SELECT periodicity, name FROM habits where periodicity = ?;''',
            [Periodicity[periodicity.upper()].value])
        return query.fetchall()

    def report_longest_streak(self, row_factory=as_dictionary):
        """
            Returns the longest run streak of all defined habits.

            Args:
                row_factory (function, optional):
                    A function that specifies how the rows returned by the database query
                    should be represented.

                    The default value is `as_dictionary`, which returns
                    the rows as dictionaries where the keys are the column names and the values
                    are the column values.

            Returns:
                list: A list of dictionaries, where each dictionary represents a row
                and the keys are the column names and the values are the column values."""
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
                SELECT name, MAX(current_streak) as "Highest Streak" FROM reports;''')
        return query.fetchall()

    def report_shortest_streak(self, row_factory=as_dictionary):
        """
           Return the shortest run streak of all defined habits.

           Args:
                row_factory (function, optional):
                    A function that specifies how the rows returned by the database query
                    should be represented.

                    The default value is `as_dictionary`, which returns
                    the rows as dictionaries where the keys are the column names and the values
                    are the column values.

           Returns:
               list: A list of dictionaries, where each dictionary represents a row
               and the keys are the column names and the values are the column values."""
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
                SELECT name, MIN(current_streak) as "Highest Streak" FROM reports WHERE 
                current_streak > 0;''')
        return query.fetchall()

    def report_longest_streak_given_habit(self, id_habit: int, row_factory=as_dictionary):
        """
        Returns the longest run streak for a given habit.

        Args:
            id_habit (int): An integer representing the ID of a habit.
            row_factory (function, optional):
                A function that specifies how the rows returned by the database query
                should be represented.

                The default value is `as_dictionary`, which returns
                the rows as dictionaries where the keys are the column names and the values
                are the column values.

        Returns:
            list: A list of dictionaries, where each dictionary represents a row
            and the keys are the column names and the values are the column values."""

        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
                SELECT name, MAX(current_streak) as "Highest Streak" 
                FROM reports where id_habit = ?;''', [id_habit])
        return query.fetchall()

    def get_habit_list_snapshot(self, row_factory=as_dictionary):
        """
        Return a snapshot of habit list.

            Args:
                row_factory (function, optional):
                    A function that specifies how the rows returned by the database query
                    should be represented.

                    The default value is `as_dictionary`, which returns
                    the rows as dictionaries where the keys are the column names and the values
                    are the column values.

            Returns:
                list: A list of dictionaries, where each dictionary represents a row
                and the keys are the column names and the values are the column values."""
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
            select id_habit, name  from reports r group by id_habit;
        ''')
        return query.fetchall()
