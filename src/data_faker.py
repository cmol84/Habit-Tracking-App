"""With this module, I am generating test data for habits, tasks and reports, and doing the
necessary timetravel to get the right amount of data for the right times in."""
import random
from datetime import datetime, timedelta

from faker import Faker

from database import Habit, Task, Report, Periodicity

fake = Faker()
Faker.seed(1)

current_time = datetime.now()
start_time = current_time - timedelta(days=30)


def main():
    """
    Perform initialization and simulation of habits, tasks, and reports.

    This function initializes habits, tasks, and simulates user interactions
    and report generation for a period of 30 days.

    Args:
        None

    Returns:
        None
    """
    print('Deleting old database entries ...')
    for report in Report.objects():
        report.delete()
    for task in Task.objects():
        task.delete()
    for habit in Habit.objects():
        habit.delete()
    # generate initial habits and first batch of tasks
    print('Generate initial habits and first batch of tasks ...')

    for periodicity in [Periodicity.DAILY, Periodicity.WEEKLY, Periodicity.MONTHLY]:
        for _ in range(10):
            habit = Habit(
                name=fake.sentence(nb_words=4),
                periodicity=periodicity,
                template=fake.texts(nb_texts=5, max_nb_chars=40),
                created_at=start_time,
                updated_at=start_time
            ).save()
            generate_tasks(habit, start_time)
    # simulate user input and report generation for the next 30 days.
    print('Simulating user input and report generation for the next 30 days ...')
    for delta in range(30):
        delta_time = start_time + timedelta(days=delta)
        task_list = list(Task.objects())
        # complete a few random tasks
        for _ in range(120):
            task = random.choice(task_list)
            task_list.remove(task)
            task.completed = True
            task.updated_at = delta_time
            task.save()
        # Create a report of the finished periodicity habits and tasks
        print(f'Create a report on day {delta_time.strftime("%Y-%m-%d")} ...')
        for habit in Habit.objects(timestamp=delta_time):
            Report(habit.id_habit, created_at=delta_time).generate()
            generate_tasks(habit, delta_time)


def generate_tasks(habit, timestamp):
    """
        Generates and saves tasks based on a given habit and timestamp.

        This function generates individual tasks from the provided habit's template and
        saves them with the specified timestamp as their creation and update time.

        Args:

            habit (Habit): The habit for which tasks need to be generated
            timestamp (datetime): The timestamp to be used for task creation and update.

        Returns:
            None

        Note:
            The provided `habit` object should have a `template` attribute containing a list
            of tasks to be generated.
        """

    for task in habit.template:
        Task(habit.id_habit, task, created_at=timestamp, updated_at=timestamp).save()


if __name__ == "__main__":
    main()
