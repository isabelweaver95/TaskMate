import csv
import json
from task import Task  # Assuming you have the Task class in task.py

class TaskDataManager:
    def __init__(self, csv_filename="tasks.csv", json_filename="tasks.json"):
        self.csv_filename = csv_filename
        self.json_filename = json_filename

    def save_to_csv(self, tasks):
        """Saves a list of Task objects to a CSV file."""
        with open(self.csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["name", "duration", "due_date", "priority", "urgency"])
            for task in tasks:
                writer.writerow([task.name, task.duration.total_seconds() / 3600, task.due_date.strftime("%Y-%m-%d"), task.priority, task.urgency])

    def load_from_csv(self):
        """Loads tasks from a CSV file and returns a list of Task objects."""
        tasks = []
        try:
            with open(self.csv_filename, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    task = Task(
                        name=row["name"],
                        duration=float(row["duration"]),
                        due_date=row["due_date"],
                        priority=row["priority"]
                    )
                    tasks.append(task)
        except FileNotFoundError:
            print("CSV file not found. Returning an empty task list.")
        return tasks

    def save_to_json(self, tasks):
        """Saves a list of Task objects to a JSON file."""
        with open(self.json_filename, mode='w') as file:
            json.dump([{
                "name": task.name,
                "duration": task.duration.total_seconds() / 3600,
                "due_date": task.due_date.strftime("%Y-%m-%d"),
                "priority": task.priority,
                "urgency": task.urgency
            } for task in tasks], file, indent=4)

    def load_from_json(self):
        """Loads tasks from a JSON file and returns a list of Task objects."""
        tasks = []
        try:
            with open(self.json_filename, mode='r') as file:
                data = json.load(file)
                for item in data:
                    task = Task(
                        name=item["name"],
                        duration=float(item["duration"]),
                        due_date=item["due_date"],
                        priority=item["priority"]
                    )
                    tasks.append(task)
        except (FileNotFoundError, json.JSONDecodeError):
            print("JSON file not found or invalid. Returning an empty task list.")
        return tasks
