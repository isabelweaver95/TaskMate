from datetime import datetime, timedelta


def get_task_info():
    '''
    This function will get the task info from the user. '''
    task_name = input("Enter the task name: ")
    time = float(input("Enter the task description in hours: "))
    priority = input("Enter the priority (low, medium, high): ")
    due_date = input("Enter the due date (YYYY-MM-DD): ")
    return {
        "task_name": task_name,
        "time": time,
        "priority": priority,
        "due_date": due_date, # Change this to a date in future. Then you can compare each task's due date
    }

def convert_to_datetime(time_str):
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

def calculate_task_end_time(start_time, time):
    '''This function will calculate the end time of the task'''
    end_time = start_time + timedelta(hours=time)

    return end_time

def fits_in_time_slot(task, start_time, end_time):
    '''This function will check if the task can be done in the time slot'''
    task_end_time = calculate_task_end_time(start_time, task["time"])
    return task_end_time <= end_time


# This function will be used to make sure the task can get done by t
def avialable_time_slot():
    '''
    This function will get the available time slot for the task, or the time slot that is available.'''
    task = get_task_info()
    start_time = input("Enter what time you are free to start the task: ") 
    end_time = input("Enter what time you are free to end the task: ")


    try:
        start_datetime = convert_to_datetime(start_time)
        end_datetime = convert_to_datetime(end_time)
    except ValueError:
        print("e")
        return
    
    if(fits_in_time_slot(task, start_datetime, end_datetime)):
        print("Task can be done")
    else:
        print("Task can't be done")


avialable_time_slot()
