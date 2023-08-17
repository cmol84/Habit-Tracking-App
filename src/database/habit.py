class Habit:
    def create_habit(self, name: str, periodicity: Periodicity, task_template: list[str]) -> dict:
        """ Creates a new habit in the database.

        Args:
            name (str): Name of the habit.
            periodicity (Periodicity): The periodicity of the habit.
            task_template (list[str]): List of task templates.

        Raises:
            sqlite3.IntegrityError: If a habit with the same name already exists in the
        database."""

        self.cursor.execute(
            '''INSERT INTO habits (name, periodicity, template) VALUES(?, ?, ?)''',
            (name, periodicity.value, json.dumps(task_template)))
        self.connection.commit()
        query = self.cursor.execute(
            '''SELECT * FROM habits where name = ?''', [name])
        return query.fetchone()

    def delete_habit(self, id_habit: int):
        """ Deletes a habit and its associated tasks from the database.

        Args:
            id_habit (int): The ID of the habit to delete."""

        self.cursor.execute('''DELETE FROM tasks WHERE id_habit = ?''', [id_habit])
        self.cursor.execute('''DELETE FROM habits WHERE id_habit = ?''', [id_habit])
        self.connection.commit()

    def select_habits_to_fulfill(self, row_factory=as_dictionary):
        """ Selects habits without associated tasks from the database.

        Args:
            row_factory (function, optional): The function to use as the row factory.
            Defaults to `as_dictionary`.

        Returns: list[dict]: A list of dictionaries representing habits without tasks."""

        self._set_row_factory(row_factory)
        query = self.cursor.execute('''
        SELECT *
        FROM habits h
        where (select count(*) from tasks where id_habit = h.id_habit) = 0;''')
        return query.fetchall()

    def select_habits(
            self,
            query_fields='id_habit, name, periodicity, streak',
            id_habit=None,
            row_factory=as_dictionary
    ):
        """ Selects all habits from the database.

        Args:
            row_factory (function, optional): The function to use as the row factory.
            Defaults to `as_dictionary`.
            query_fields: string of fields to select from the habits table
            id_habit: number or None to filter the query by id

        Returns: list[dict]: A list of dictionaries representing habits.
        """
        self._set_row_factory(row_factory)
        statement = f'SELECT {query_fields} FROM habits '
        if id_habit is not None:
            statement += 'where id_habit = ?'
            query = self.cursor.execute(statement, [id_habit])
            return query.fetchall()
        query = self.cursor.execute(statement)
        return query.fetchall()
