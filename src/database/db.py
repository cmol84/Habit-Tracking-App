"""
The database module: Primarily creates database tables, stores information and returns data.
"""
import enum
import sqlite3
import json
from faker import Faker

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
    fields = [column[0] for column in cursor.description]
    return zip(fields, row)


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
                id_habit INTEGER PRIMARY KEY, 
                name TEXT NOT NULL UNIQUE, 
                periodicity TEXT, 
                streak INT DEFAULT 0,
                template TEXT NOT NULL, 
                created_at timestamp DATE DEFAULT (datetime('now','localtime')), 
                updated_at timestamp DATE DEFAULT (datetime('now','localtime'))
           )''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id_task INTEGER PRIMARY KEY, 
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
                id_report INTEGER PRIMARY KEY, 
                id_habit INTEGER NOT NULL, 
                name NOT NULL,
                streak INT,
                completed BOOL NOT NULL,
                created_at timestamp DATE DEFAULT (datetime('now','localtime')),
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

    def select_executable_habits(self, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
        SELECT h.*, 
        (select count(*) from tasks where id_habit = h.id_habit) as task_count
        FROM habits h;''')
        return query.fetchall()

    def select_habits(self, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
            SELECT id_habit, name, periodicity, streak FROM habits;''')
        return query.fetchall()

    def select_tasks(self, row_factory=as_dictionary):
        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
            SELECT t.id_task, h.name, t.task, t.completed 
            FROM tasks t
            join habits h on t.id_habit = h.id_habit ;''')
        return query.fetchall()

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
            '''UPDATE tasks set completed = 1 where id_task = ?''',
            [id_task]
        )
        self.connection.commit()


if __name__ == "__main__":
    db = DB()
    for habit in db.select_executable_habits():
        print(habit)

    # cleaning = ["Take out Trash", "Vacuum", "Clear dust"]
    # workout = ["Walk", "Cycling", "Gym"]
    # sleep = ["Stop caffeine intake after 12", "Wind down", "Practice relaxation", "Set 8 hours "
    #                                                                               "interval"]
    # meditate = ["Disconnect", "De-stress", "Move to quiet place", "Meditate"]
    # db.create_habit("Cleaning", Periodicity.WEEKLY, cleaning)
    # db.create_habit("Workout", Periodicity.DAILY, workout)
    # db.create_habit("Sleep", Periodicity.DAILY, sleep)
    # db.create_habit("Meditate", Periodicity.DAILY, meditate)
