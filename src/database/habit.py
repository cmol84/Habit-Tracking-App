import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generator, Self

from .db import DB, DATE_FORMAT
from .types import Periodicity


@dataclass
class Habit:
    """
    Represents a habit with associated properties.

    Attributes:
        name (str): The name of the habit.
        periodicity (Periodicity): The periodicity of the habit (e.g., daily, weekly).
        template (List[str]): List of strings representing the habit's template.
        streak (int, optional): The current streak of the habit. Defaults to 0.
        created_at (datetime, optional): The timestamp when the habit was created.
        Defaults to the current datetime.
        updated_at (datetime, optional): The timestamp when the habit was last updated.
        Defaults to the current datetime.
        id_habit (int, optional): The unique ID of the habit. Defaults to None.
        db (DB, optional): The database instance associated with the habit.
        Defaults to a new DB instance.

    Note:
        - The `periodicity` attribute should be an instance of the `Periodicity` class.
        - The `template` attribute should be a list of strings representing the habit's template.
        - The `created_at` and `updated_at` attributes are automatically set to the current datetime
        - The `db` attribute is an instance of the `DB` class, used for database operations.
    """

    name: str
    periodicity: Periodicity
    template: list[str]
    streak: int = 0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    id_habit: int = None
    db: DB = DB()

    @staticmethod
    def objects(
            no_tasks=False,
            filter_habit=None,
            finished=False,
            timestamp=datetime.now(),
            db: DB = DB()
    ) -> Generator:
        """
        Retrieve habits from the database.

        This static method retrieves habits from the database, optionally filtering
        based on whether habits have associated tasks or not.

        Args:
            no_tasks (bool, optional): If True, filter habits with no associated tasks.
                Defaults to False.
            db (DB, optional): Database connection object. Defaults to DB().
            filter_habit: Defined query filter.
            finished: selects finished habits, regardless of state.
            timestamp: datetime=datetime.now(): internal override for test data generation

        Yields:
            Generator: A generator yielding instances of Habit mapped from the database rows.

        Note:
            The `DB` class is assumed to be defined and available.

        Returns:
            Generator: A generator yielding instances of Habit.
        """
        q_filter = []
        if no_tasks:
            q_filter.append('(select count(*) from tasks '
                            'where id_habit = h.id_habit) = 0')

        if filter_habit:
            q_filter.append(f'id_habit = {filter_habit.id_habit}')

        if finished:
            past_day = timestamp - timedelta(days=1)
            past_week = timestamp - timedelta(days=7)
            past_month = timestamp - timedelta(days=30)
            q_filter.append(f'''
            (
                (updated_at <= '{past_day.strftime(DATE_FORMAT)}'
                    and periodicity = '{Periodicity.DAILY}')
                or
                (updated_at <= '{past_week.strftime(DATE_FORMAT)}'
                    and periodicity = '{Periodicity.WEEKLY}')
                or
                (updated_at <= '{past_month.strftime(DATE_FORMAT)}'
                    and periodicity = '{Periodicity.MONTHLY}')
                or
                (select count(*) from tasks 
                where completed is not TRUE and id_habit = h.id_habit) = 0 
            )
            ''')

        where = f'where {" and ".join(q_filter)}' if len(q_filter) > 0 else ''
        query = db.cursor.execute(f'SELECT * FROM habits h {where}')
        for row in query.fetchall():
            yield Habit._map_db(row, db=db)

    @staticmethod
    def _map_db(row, db: DB = DB()):
        """
        Maps a database row to a Habit object.

        This static method takes a database row dictionary and constructs a Habit
        object from the provided data.

        Args:
            row (dict): A dictionary representing a database row containing habit information.

        Yields:
            Habit: A Habit object constructed from the data in the database row.

        Returns:
            None

        Raises:
            ValueError: If the data in the row is not formatted correctly."""
        return Habit(
            name=row.get('name'),
            periodicity=Periodicity(row.get('periodicity')),
            template=row.get('template'),
            id_habit=row.get('id_habit'),
            streak=row.get('streak'),
            created_at=datetime.strptime(row.get('created_at'), DATE_FORMAT),
            updated_at=datetime.strptime(row.get('updated_at'), DATE_FORMAT),
            db=db,
        )

    @staticmethod
    def get(id_habit: int, db: DB = DB()):
        """
            Retrieve a Habit object from the database based on the given habit ID.

            Parameters:
            - id_habit (int): The ID of the habit to retrieve.
            - db (DB, optional): The database connection. Defaults to a new DB instance.

            Returns:
            Habit or None: A Habit object representing the retrieved habit if found,
            or None if not found."""

        query = db.cursor.execute(
            '''SELECT * FROM habits where id_habit = ?''',
            [id_habit]
        )
        row = query.fetchone()
        return Habit._map_db(row, db=db)

    def as_tabulate(self) -> list:
        """
            Generates a tabulated representation of the Habit object's information and summary.

            This method queries the database to retrieve summary information about
            the Habit's tasks, including the total number of tasks and the number of completed
            tasks. It then constructs a list containing various attributes of the Habit
            object along with the retrieved summary.

            Returns:
                list: A list containing the following information in order:

                - Habit ID
                - Habit name
                - Habit periodicity value
                - Habit streak
                - Total number of tasks associated with the Habit
                - Number of completed tasks associated with the Habit
            """

        select = self.db.cursor.execute(
            '''SELECT COUNT(*) as tasks, sum(completed) as tasks_completed 
            from tasks where id_habit = ? ''', [self.id_habit])
        summary = select.fetchone()
        return [self.id_habit, self.name, self.periodicity.value, self.streak,
                summary.get('tasks'), summary.get('tasks_completed')]

    def save(self) -> Self:
        """
            Saves the current habit instance to the database.

            This method inserts the habit's information into the 'habits' table
            of the database, including its name, periodicity, template, ID,
            streak, creation and update timestamps.

            Returns:
                Self: The updated habit instance after saving.

            Raises:
                DatabaseError: If there's an issue with executing the database
                queries or committing changes.
            """
        value_list = [
            self.name,
            self.periodicity.value,
            json.dumps(self.template),
            self.id_habit,
            self.streak,
            self.created_at.strftime(DATE_FORMAT),
            self.updated_at.strftime(DATE_FORMAT)
        ]
        if self.id_habit is not None:
            value_list.append(self.id_habit)
            self.db.cursor.execute(
                '''UPDATE habits SET name=?, periodicity=?, template=?, id_habit=?, streak=?, 
                created_at=?, updated_at=? 
                where id_habit=?''', value_list
            )
        else:
            self.db.cursor.execute(
                '''REPLACE INTO habits 
                (name, periodicity, template, id_habit, streak, created_at, updated_at) 
                VALUES(?, ?, ?, ?, ?, ?, ?)''',
                value_list
            )
        self.db.connection.commit()

        query = self.db.cursor.execute(
            '''SELECT * FROM habits where name = ?''', [self.name])
        raw_data = query.fetchone()
        self.id_habit = raw_data.get('id_habit')
        return self

    def delete(self) -> Self:
        """
        Deletes the current instance from the database.

        This method deletes the instance's data from the associated database tables
        ('tasks' and 'habits') based on the 'id_habit' value. It raises a ReferenceError
        if the instance has not been saved (i.e., 'id_habit' is None). After successful
        deletion, the database changes are committed, and the method returns the updated
        instance.

        Returns:
            Self: The updated instance after deletion.

        Raises:
            ReferenceError: If the instance has not been saved yet."""
        if self.id_habit is None:
            raise ReferenceError(
                'This instance has not been saved yet so you cannot delete it!')
        self.db.cursor.execute(
            '''DELETE FROM tasks WHERE id_habit = ?''',
            [self.id_habit]
        )
        self.db.cursor.execute(
            '''DELETE FROM habits WHERE id_habit = ?''',
            [self.id_habit]
        )
        self.db.connection.commit()
        return self
