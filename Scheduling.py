from datetime import datetime, timedelta
from task import Task

class Scheduler:
    def __init__(self, tasks, start_time, end_time):
        self.tasks = tasks
        self.breaks = False
        self.start_time = start_time
        self.end_time = end_time

    def add_task(self, task):
        self.tasks.append(task)

    def sort_tasks(self):
        self.tasks.sort(key=lambda x: x.urgency, reverse=True)  # Sort tasks by urgency

    def schedule_tasks(self):
        self.sort_tasks()
        for task in self.tasks:
            print(f"Task: {task.name}, Urgency: {task.urgency}, Due Date: {task.due_date}")

    def calculate_task_end_time(self, start_time, duration):
        '''Calculate the end time of a task'''
        return start_time + duration

    def fits_in_time_slot(self, task, current_time):
        '''Check if the task can be done in the given time slot'''
        task_end_time = self.calculate_task_end_time(current_time, task.time)
        return task_end_time <= self.end_time

    def check_if_task_can_be_done(self, task, current_time):
        '''Check if a task can be completed within the scheduler's timeframe'''
        return self.fits_in_time_slot(task, current_time)

    def calculate_amount_of_time(self):
        '''Calculate the amount of time required to complete all tasks'''

        incomplete_tasks = []  # Tasks that cannot be completed
        completed_tasks = []   # Tasks that can be completed

        current_time = self.start_time  # Track task start time

        for task in list(self.tasks):  # Iterate over a copy of the list to avoid issues
            task_duration = task.time  # Convert task time to timedelta

            if self.fits_in_time_slot(task, current_time):
                print(f"'{task.name}' will start at {current_time.strftime('%H:%M')}")
                current_time += task_duration
                completed_tasks.append(task)
                print(f"'{task.name}' will end at {current_time.strftime('%H:%M')}")
            else:
                incomplete_tasks.append(task)

        return completed_tasks, incomplete_tasks