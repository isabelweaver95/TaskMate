from datetime import datetime, timedelta
import task

class Scheduler:
    def __init__(self, tasks, start_time, end_time):
        self.tasks = tasks
        self.breaks = False
        self.start_time = self.convert_to_datetime(start_time)
        self.end_time = self.convert_to_datetime(end_time)

    def add_task(self, task):
        self.tasks.append(task)

    def sort_tasks(self):
        self.tasks.sort(key=lambda x: x.urgency, reverse=True)  # Sort tasks by urgency

    def schedule_tasks(self):
        self.sort_tasks()
        for task in self.tasks:
            print(f"Task: {task.name}, Urgency: {task.urgency}, Due Date: {task.due_date}")

def convert_to_datetime(self, time_str):
    '''This converts the time string to a datetime object. 
    The time string should be in the format "HH:MM" or "HH:MM AM/PM" '''

    time_str = time_str.strip()

    try:
        return datetime.strptime(time_str, "%H:%M")
    except ValueError:
        try:
            return datetime.strptime(time_str, "%I:%M %p")
        except ValueError:
            raise ValueError("Invalid time format")
    

    return datetime.strptime(time_str, "%H:%M")