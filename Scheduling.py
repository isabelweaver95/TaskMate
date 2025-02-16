from datetime import datetime, timedelta
import task

class Scheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def sort_tasks(self):
        self.tasks.sort(key=lambda x: x.urgency, reverse=True)  # Sort tasks by urgency

    def schedule_tasks(self):
        self.sort_tasks()
        for task in self.tasks:
            print(f"Task: {task.name}, Urgency: {task.urgency}, Due Date: {task.due_date}")