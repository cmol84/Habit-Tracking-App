"""
The database module: Primarily creates database tables, stores information and returns data.
"""
import enum
import sqlite3
import json
from faker import Faker
from typing import List

fake = Faker(['en_US'])
Faker.seed(1)


class Periodicity(enum.Enum):
    DAILY = 'Every Day'
    WEEKLY = 'Every Week'
    MONTHLY = 'Every Month'


def as_dictionary(cursor, row):
    fields = [column[0] for column in cursor.description]
    data = {key: value for key, value in zip(fields, row)}
    if 'template' in data:
        data['template'] = json.loads(data.get('template'))
    return data


def as_array(cursor, row):
    return row


class DB:

    def __init__(self, name="habit_tracking_app.db"):
        """
        Function to create and maintain connection with database.
        :param name: Name of the database to create or connect with (default habit_tracking_app.db)
        :return: Returns the database connection
        """
        self.connection = sqlite3.connect(name)
        self._set_row_factory()
        self._migrate()

    def _migrate(self):
        """
        Creates three database tables: namely 'habits', 'tasks' and 'reports'.
        The 'habits' table consists of the following  columns: id_habit, Name, Periodicity, Streak,
        Template - json, Created_at, Updated_at
        The 'tasks' table contains the following columns: id_task, id_habit, Task, Completed,
        Created_at, Updated_at
        The 'reports' table will contain the following columns: id_report, id_habit, Name,
        Streak, Completed, Created_at.
        """

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
        self.connection.row_factory = row_factory
        self.cursor = self.connection.cursor()

    def create_habit(self, name: str, periodicity: Periodicity, task_template: list[str]):
        self.cursor.execute('''INSERT INTO habits (name, periodicity, template) VALUES(?, ?, 
        ?)''', (name, periodicity.value, json.dumps(task_template)))
        self.connection.commit()

    def delete_habit(self, id_habit: int):
        self.cursor.execute('''DELETE FROM tasks WHERE id_habit = ?''', [id_habit])
        self.cursor.execute('''DELETE FROM habits WHERE id_habit = ?''', [id_habit])
        self.connection.commit()

    def select_habits_to_fulfill(self, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
        SELECT *
        FROM habits h
        where (select count(*) from tasks where id_habit = h.id_habit) = 0;''')
        return query.fetchall()

    def select_habits(self, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
            SELECT id_habit, name, periodicity, streak FROM habits;''')
        return query.fetchall()

    def select_tasks(self, id_habit=None, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        statement = '''SELECT t.id_task, h.name, t.task, t.completed 
            FROM tasks t
            JOIN habits h on t.id_habit = h.id_habit
            '''
        if id_habit is not None:
            statement += 'where t.id_habit = ?;'
            query = self.cursor.execute(statement, [id_habit])

            return query.fetchall()

        query = self.cursor.execute(statement)
        return query.fetchall()

    def check_task_status(self, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
            SELECT
                h.id_habit 
                , h.name 
                , h.streak
                , (select count(*) from tasks where completed is TRUE and id_habit = h.id_habit)
                as completed_tasks_count
                , (select count(*) from tasks where completed is not TRUE and id_habit = h.id_habit)
                as uncompleted_tasks_count
            FROM
                habits h
            where
                (updated_at <= datetime('now', '-1 DAY', 'LOCALTIME')
                    and periodicity = 'Every Day')
                or
            (updated_at <= datetime('now', '-1 WEEK', 'LOCALTIME')
                    and periodicity = 'Every Week')
                or
            (updated_at <= datetime('now', '-1 MONTH', 'LOCALTIME')
                    and periodicity = 'Every Month')
                or
            (select count(*) from tasks where completed is not TRUE and id_habit = h.id_habit) = 0; 
        ''')
        return query.fetchall()

    def generate_report(self, habit: dict, task_list: List[dict]):
        id_habit = habit.get('id_habit')
        self.cursor.execute(
            '''INSERT INTO reports (id_habit, name, current_streak, completed_tasks_count, 
            uncompleted_tasks_count, raw_data) VALUES (?, ?, ?, ?, ?, ?)''',
            (
                id_habit,
                habit.get('name'),
                habit.get('current_streak'),
                habit.get('completed_tasks_count'),
                habit.get('uncompleted_tasks_count'),
                json.dumps(task_list))
        )
        self.connection.commit()

        self.cleanup_tasks(id_habit)

        if habit.get('uncompleted_tasks_count') == 0:
            self.bump_streak(id_habit)
            return

        self.reset_streak(id_habit)

    def create_task(self, id_habit: int, task: str):
        self.cursor.execute(
            '''INSERT INTO tasks (id_habit, task) VALUES (?, ?)''',
            (id_habit, task)
        )
        self.cursor.execute(
            '''UPDATE habits set updated_at = datetime('now', 'localtime') where id_habit = ?''',
            [id_habit]
        )
        self.connection.commit()

    def update_completed(self, id_task: int):
        self.cursor.execute(
            '''UPDATE tasks set completed = 1, updated_at = datetime('now', 'localtime') where 
            id_task = ?''',
            [id_task]
        )
        self.connection.commit()

    def bump_streak(self, id_habit: int):
        self.cursor.execute(
            '''UPDATE habits set streak = streak +1, updated_at = datetime('now', 'localtime') 
            where id_habit = ?''', [id_habit]
        )
        self.connection.commit()

    def reset_streak(self, id_habit: int):
        self.cursor.execute(
            '''UPDATE habits set streak = 0, updated_at = datetime('now', 'localtime') 
            where id_habit = ?''', [id_habit]
        )
        self.connection.commit()

    def cleanup_tasks(self, id_habit: int):
        self.cursor.execute('''DELETE FROM tasks WHERE id_habit = ?''', [id_habit])
        self.connection.commit()

    """
    Returns a list of all currently tracked habits. 
    This will already be covered by the list habits function.
    """

    def report_same_period(self, periodicity: str, row_factory=as_dictionary):
        """
        Report that returns a list of all habits with the same periodicity.
        """
        self._set_row_factory(row_factory)
        query = self.cursor.execute(
            '''SELECT periodicity, name FROM habits where periodicity = ?;''',
            [Periodicity[periodicity.upper()].value])
        return query.fetchall()

    def report_longest_streak(self, row_factory=as_dictionary):
        """
        Return the longest run streak of all defined habits.
        """
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
                SELECT name, MAX(current_streak) as "Highest Streak" FROM reports;''')
        return query.fetchall()

    def report_shortest_streak(self, row_factory=as_dictionary):
        """
        Return the shortest run streak of all defined habits.
        """
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
                SELECT name, MIN(current_streak) as "Highest Streak" FROM reports WHERE 
                current_streak > 0;''')
        return query.fetchall()

    def report_longest_streak_given_habit(self, id_habit: int, row_factory=as_dictionary):
        """
        Returns the longest run streak for a given habit.
        """
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
                SELECT name, MAX(current_streak) as "Highest Streak" 
                FROM reports where id_habit = ?;''', [id_habit])
        return query.fetchall()

    def get_habit_list_snapshot(self, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
            select id_habit, name  from reports r group by id_habit;
        ''')
        return query.fetchall()
