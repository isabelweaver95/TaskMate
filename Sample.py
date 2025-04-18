from datetime import datetime, timedelta
from task import Task
from Scheduling import Scheduler

def get_task_info():
    '''
    This function will get the task info from the user. '''

    task_name = input("Enter the task name: ")
    time = float(input("Enter the task description in hours: "))
    priority = input("Enter the priority (low, medium, high): ")
    due_date = input("Enter the due date (YYYY-MM-DD): ")

    task = Task(task_name, time, due_date, priority)
    return task

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
    end_time = start_time + time

    return end_time

def fits_in_time_slot(task, start_time, end_time):
    '''This function will check if the task can be done in the time slot'''
    task_end_time = calculate_task_end_time(start_time, task.time)
    return task_end_time <= end_time


# This function will be used to make sure the task can get done by t
def avialable_time_slot():
    '''
    This function will get the available time slot for the task, or the time slot that is available.'''

    start_time = input("Enter what time you are free to start the task: ") 
    end_time = input("Enter what time you are free to end the task: ")


    try:
        start_datetime = convert_to_datetime(start_time)
        end_datetime = convert_to_datetime(end_time)
    except ValueError:
        print("e")
        return

    return start_datetime, end_datetime


def check_if_task_can_be_done(task, start_datetime, end_datetime):
    if(fits_in_time_slot(task, start_datetime, end_datetime)):
        return True
    else:
        return False


def calculate_amount_of_time(tasks, start_datetime, end_datetime):
    '''This function will calculate the amount of time it will take to complete all tasks'''

    tasks.sort_tasks()

    incomplete_tasks = []  # Array to hold tasks that cannot be done in the time slot
    completed_tasks = Scheduler()   # Array to hold tasks that can be done in the time slot

    for task in tasks.tasks:  # Iterate over a copy of the list to avoid issues while modifying
        amount_task_time = task.time

        if check_if_task_can_be_done(task, start_datetime, end_datetime):
            print(f"'{task.name}' will start at {start_datetime}")
            start_datetime += amount_task_time
            completed_tasks.add_task(task)
            print(f"'{task.name}' will end at {start_datetime.strftime('%H:%M')}")
        else:
            #print(f"The task '{task.name}' cannot be done in the time slot.")
            incomplete_tasks.append(task)
            tasks.tasks.remove(task)  # Remove the task from the original list
    

    return completed_tasks, incomplete_tasks

def start_loop():
    tasks = []
    loops = int(input("Enter the number of tasks you would like to schedule: "))
    
    for _ in range(loops):
        task = get_task_info()  # Get task info from the user
        tasks.append(task)

    return tasks


def main():
    '''Main function to run the program'''
    tasks = start_loop()
    start_datetime, end_datetime = avialable_time_slot()
    schedule = Scheduler(tasks, start_datetime, end_datetime)
    schedule.calculate_amount_of_time()


if __name__ == "__main__":
    main()
