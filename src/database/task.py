from dataclasses import dataclass
from datetime import datetime
from typing import Generator, Self

from .db import DB, DATE_FORMAT
from .habit import Habit


@dataclass
class Task:
    """
        Represents a task associated with a habit.

        Attributes:
            id_habit (int): The ID of the habit to which the task belongs.
            task (str): The description of the task.
            completed (bool, optional): Indicates whether the task is completed (default is False).
            id_task (int, optional): The unique ID of the task (default is None).
            created_at (datetime, optional): The timestamp of task creation
                (default is the current datetime).
            updated_at (datetime, optional): The timestamp of task last update
                (default is the current datetime).
            db (DB, optional): The database connection instance (default is a new instance of DB()).

        Methods:
            habit(self) -> Habit:
                Retrieves the associated Habit object for this task.

            objects(habit: Habit = None, db: DB = DB()) -> Generator:
                Generator that yields Task instances filtered by habit.

            _map_task(row) -> Generator:
                Maps a database row to a Task instance.

            save(self) -> Self:
                Saves the task instance to the database.

            from_habit(habit: Habit, db: DB = DB()):
                Creates and saves tasks based on a Habit's template.

            get(id_task: int, db: DB = DB()) -> Task:
                Retrieves a Task instance based on its ID."""

    id_habit: int
    task: str
    completed: bool = False
    id_task: int = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    db: DB = DB()

    def habit(self) -> Habit:
        """
        Retrieve a Habit object based on the provided `id_habit` using the given database connection

        This method fetches a Habit object from the database using the specified `id_habit` and
        database connection (`db`). It returns the corresponding Habit object if found, or None if
        no such Habit with the provided `id_habit` exists in the database.

        Parameters:
        self (object): The instance of the class containing the `habit` method.

        Returns:
        Habit: A Habit object representing the habit retrieved from the database,
        or None if not found.
        """
        return Habit.get(id_habit=self.id_habit, db=self.db)

    @staticmethod
    def objects(habit: Habit = None, db: DB = DB()) -> Generator:
        """
        Retrieve tasks from the database based on the provided habit or retrieve
        all tasks if no habit is provided.

        Args:
            habit (Habit, optional): The habit for which to retrieve tasks.
                If not provided, all tasks will be retrieved.
            db (DB, optional): The database connection to use. Defaults to a new DB instance.

        Yields:
            Generator: A generator that yields mapped Task instances retrieved from the database."""

        if isinstance(habit, Habit):
            query = db.cursor.execute(
                'SELECT * FROM tasks where id_habit = ?',
                [habit.id_habit]
            )
        else:
            query = db.cursor.execute('SELECT * FROM tasks')
        for row in query.fetchall():
            yield Task._map_task(row, db=db)

    @staticmethod
    def _map_task(row, db: DB = DB()):
        """
            Maps a row from a data source to a Task object.

            This static method takes a dictionary-like 'row' object representing a task's
            attributes and generates a Task object with the provided information.

            Args:
                row (dict): A dictionary containing task information.

            Yields:
                Task: A Task object created from the provided row data.

            Raises:
                ValueError: If any required fields are missing in the 'row' or
                    if there's a date parsing error.

            Returns:
                Generator[Task, None, None]: A generator yielding a Task object."""

        return Task(
            id_task=row.get('id_task'),
            id_habit=row.get('id_habit'),
            task=row.get('task'),
            completed=row.get('completed'),
            created_at=datetime.strptime(row.get('created_at'), DATE_FORMAT),
            updated_at=datetime.strptime(row.get('updated_at'), DATE_FORMAT),
            db=db
        )

    def save(self) -> Self:
        """
        Save the current task instance to the database.

        This method inserts a new task record into the 'tasks' table with the provided
        attributes. After inserting the record, the task's `id_task` attribute is updated
        with the generated ID from the database. The method then returns the updated task
        instance.

        Returns:
            Self: The updated task instance with the `id_task` attribute populated.

        Raises:
            DatabaseError: If there is an issue with executing the SQL queries or committing
                          the transaction.

        Note:
            This method assumes that the 'tasks' table has the following columns:
            - id_habit: ID of the associated habit
            - task: Task description
            - completed: Task completion status
            - id_task: Task ID (auto-generated by the database)
            - created_at: Timestamp of task creation
            - updated_at: Timestamp of task's last update

        Usage:
            task = Task(id_habit=1, task='Do something', completed=False)
            task.save()
        """

        self.db.cursor.execute(
            '''REPLACE INTO tasks 
            (id_habit, task, completed, id_task, created_at, updated_at) 
            VALUES(?, ?, ?, ?, ?, ?)''',
            (self.id_habit, self.task, self.completed, self.id_task,
             self.created_at.strftime(DATE_FORMAT),
             self.updated_at.strftime(DATE_FORMAT)))
        self.db.connection.commit()
        query = self.db.cursor.execute(
            '''SELECT * FROM tasks where id_habit = ? and task = ?;''',
            [self.id_habit, self.task])
        raw_data = query.fetchone()
        self.id_task = raw_data.get('id_task')
        return self

    @staticmethod
    def from_habit(habit: Habit, db: DB = DB()):
        """
        Create and save Task instances based on the tasks defined in a Habit's template.

        This static method takes a Habit object and an optional DB object as parameters. It
        iterates through the tasks defined in the habit's template and creates corresponding
        Task instances.
        Each Task instance is associated with the provided Habit's ID and the
        task description from the template.
        The Task instances are then saved to the specified database.

            Parameters:
                - habit (Habit): The Habit object containing the template of tasks
                  to be converted into Task instances.
                - db (DB, optional): The DB object representing the database to
                  which the generated Task instances will be saved.
                  If not provided, a new DB instance will be created.

        Returns:
        None

        Note:
        Make sure to have the appropriate Task and Habit classes defined before using this method.
        """
        for task in habit.template:
            Task(habit.id_habit, task, db=db).save()

    @staticmethod
    def get(id_task: int, db: DB = DB()):
        """
        Retrieve a task from the database by its ID.

        Args:
            id_task (int): The ID of the task to retrieve.
            db (DB, optional): The database connection. Defaults to a new instance of DB().

        Returns:
            Task or None:
            The Task object representing the retrieved task if found, or None if not found
        """

        query = db.cursor.execute(
            '''SELECT * FROM tasks where id_task = ?''',
            [id_task]
        )
        row = query.fetchone()
        return Task._map_task(row, db=db)

    def to_json(self):
        return {
            'id_habit': self.id_habit,
            'task': self.task,
            'completed': self.completed,
            'id_task': self.id_task,
            'created_at': self.created_at.strftime(DATE_FORMAT),
            'updated_at': self.updated_at.strftime(DATE_FORMAT),
        }

    def delete(self):
        if self.id_task is None:
            raise ReferenceError(
                'This instance has not been saved yet so you cannot delete it!')
        self.db.cursor.execute(
            '''DELETE FROM tasks WHERE id_task = ?''',
            [self.id_task]
        )
        self.db.connection.commit()
        return self
