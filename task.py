from datetime import datetime, timedelta

class Task:
    PRIORITY_MAP = {"high": 3, "medium": 2, "low": 1}  # Mapping priority to numeric values

    def __init__(self, name, due_date, priority, category):
        self.name = self.validate_name(name)
        self.priority = self.validate_priority(priority)
        self.due_date = self.convert_to_datetime(due_date)
        self.urgency = self.calculate_urgency()
        self.category = category


    @staticmethod
    def validate_name(name):
        """Ensure task name is not empty."""
        if not name.strip():
            raise ValueError("Task name cannot be empty.")
        return name

    @staticmethod
    def validate_duration(time):
        """Ensure duration is a positive number. and can be a timedelt object"""
        try:
            time = float(time)
            time = timedelta(hours=time)
        except ValueError:
            raise ValueError("Invalid duration. Enter a number greater than 0.")
        return time

    @staticmethod
    def validate_priority(priority):
        """Ensure priority is one of the allowed values (low, medium, high)."""
        priority = priority.lower()
        if priority not in Task.PRIORITY_MAP:
            raise ValueError("Invalid priority. Choose from: high, medium, low.")
        return priority

    @staticmethod
    def convert_to_datetime(date_str):
        """Convert a date string to a datetime object. Supports multiple formats."""
        formats = ["%m/%d/%y", "%m.%d.%y", "%Y-%m-%d"]  # Example: "12/31/24", "12.31.24", "2024-12-31"
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError("Invalid date format. Use 'MM/DD/YY', 'MM.DD.YY', or 'YYYY-MM-DD'.")

    def calculate_urgency(self):
        """Calculate urgency based on priority and due date. This will be 0-1. The higher the number, the more urgent."""
        days_until_due = (self.due_date - datetime.today()).days
        priority_value = self.PRIORITY_MAP.get(self.priority, 1)  # Default to low priority

        # Prevent division by zero (if due today)
        days_until_due = max(days_until_due, 1)

        return priority_value / (days_until_due + priority_value)  # Higher value means more urgent



