import csv
import json
import os

class TaskDataManager:
    def __init__(self, csv_filename="tasks.csv", json_filename="tasks.json"):
        self.csv_filename = csv_filename
        self.json_filename = json_filename

    def save_to_csv(self, tasks):
        """Save tasks to a CSV file."""
        with open(self.csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["name", "duration", "due_date", "priority", "urgency"])  # Header
            for task in tasks:
                writer.writerow([task.name, task.duration.total_seconds() / 3600, task.due_date.strftime('%Y-%m-%d'), task.priority, task.urgency])

    def save_to_json(self, tasks):
        """Save tasks to a JSON file."""
        with open(self.json_filename, mode='w') as file:
            json.dump([{ "name": task.name, "duration": task.duration.total_seconds() / 3600,
                         "due_date": task.due_date.strftime('%Y-%m-%d'), "priority": task.priority, "urgency": task.urgency}
                       for task in tasks], file, indent=4)

    def load_from_csv(self):
        """Load tasks from a CSV file."""
        tasks = []
        if os.path.exists(self.csv_filename):
            with open(self.csv_filename, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    tasks.append(row)
        return tasks

    def load_from_json(self):
        """Load tasks from a JSON file."""
        if os.path.exists(self.json_filename):
            with open(self.json_filename, mode='r') as file:
                return json.load(file)
        return []

    def append_task(self, task):
        """Append a new task to both CSV and JSON files."""
        # Append to CSV
        file_exists = os.path.exists(self.csv_filename)
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["name", "duration", "due_date", "priority", "urgency"])  # Write header if new file
            writer.writerow([task.name, task.duration.total_seconds() / 3600, task.due_date.strftime('%Y-%m-%d'), task.priority, task.urgency])
        
        # Append to JSON
        tasks = self.load_from_json()
        tasks.append({ "name": task.name, "duration": task.duration.total_seconds() / 3600,
                       "due_date": task.due_date.strftime('%Y-%m-%d'), "priority": task.priority, "urgency": task.urgency})
        self.save_to_json(tasks)

    def save_tasks(self, tasks):
        self.save_to_csv(tasks)
        self.save_to_json(tasks)

    def load_tasks(self):
        return self.load_from_csv(), self.load_from_json()
    
    