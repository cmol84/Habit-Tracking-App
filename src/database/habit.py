class Habit:
    def save(self):
        """
        Here we want to access the database and save the current instance of the habit. If the
        habit doesn't exist it's created otherwise it will be updated.
        When the datastore doesn't exist, we create it and save the habit in it.
        """
