from dataclasses import dataclass
from .habit import Habit
from .task import Task
from datetime import datetime
from .db import DATE_FORMAT, DB
import json


@dataclass
class Report:
    id_habit: int
    id_report: int = None
    name: str = None
    current_streak: int = None
    completed_tasks_count: int = None
    uncompleted_tasks_count: int = None
    created_at: datetime = datetime.now()
    raw_data: dict = None
    db: DB = DB()

    def save(self):
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
