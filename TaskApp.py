
# # from flask import Flask, request, render_template
# # from datetime import datetime
# # from TaskDurationPredictor import TaskDurationPredictor
# # from task import Task  # Import Task to access PRIORITY_MAP
# # import logging
# # from Scheduling import Scheduler
# # from datetime import datetime, timedelta
# # app = Flask(__name__)

# # # Initialize the predictor
# # predictor = TaskDurationPredictor()

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # Ensure model is trained at startup
# # if not hasattr(predictor.model, 'estimators_'):
# #     logger.info("Initializing model...")
# #     try:
# #         if predictor.train():
# #             logger.info("Model trained successfully")
# #         else:
# #             logger.error("Model training failed - predictions will not work")
# #     except Exception as e:
# #         logger.error(f"Model initialization failed: {str(e)}")

# # @app.route("/", methods=["GET", "POST"])
# # def home():
# #     if request.method == "POST":
# #         try:
# #             # Check if this is the initial form or task submission
# #             if 'total_tasks' in request.form:
# #                 # This is the multi-task submission
# #                 total_tasks = int(request.form.get("total_tasks", 0))
# #                 time_period = float(request.form.get("time_period", 0))
                
# #                 if total_tasks <= 0:
# #                     raise ValueError("Number of tasks must be at least 1")
# #                 if time_period <= 0:
# #                     raise ValueError("Time period must be positive")
                
# #                 predictions = []
                
# #                 for i in range(total_tasks):
# #                     # Get and validate form data for each task
# #                     task_name = request.form.get(f"task_name_{i}", "").strip()
# #                     due_date_str = request.form.get(f"due_date_{i}", "")
# #                     priority = request.form.get(f"priority_{i}", "").lower()
# #                     category = request.form.get(f"category_{i}", "").lower()

# #                     # Basic validation
# #                     if not task_name:
# #                         raise ValueError(f"Task name is required for task {i+1}")
# #                     if not due_date_str:
# #                         raise ValueError(f"Due date is required for task {i+1}")
# #                     if not priority:
# #                         raise ValueError(f"Priority is required for task {i+1}")
# #                     if not category:
# #                         raise ValueError(f"Category is required for task {i+1}")

# #                     # Parse and validate due date
# #                     try:
# #                         due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
# #                         if due_date < datetime.today():
# #                             raise ValueError(f"Due date cannot be in the past for task {i+1}")
# #                     except ValueError as e:
# #                         raise ValueError(f"Invalid date format for task {i+1}. Please use YYYY-MM-DD") from e

# #                     # Calculate urgency using Task's PRIORITY_MAP
# #                     days_until_due = (due_date - datetime.today()).days
# #                     days_until_due = max(days_until_due, 1)  # Prevent division by zero
# #                     urgency = Task.PRIORITY_MAP[priority] / (days_until_due + Task.PRIORITY_MAP[priority])

# #                     # Prepare task data for prediction
# #                     task_data = {
# #                         "priority": priority,
# #                         "category": category,
# #                         "urgency": urgency
# #                     }

# #                     # Make prediction
# #                     try:
# #                         predicted_minutes = predictor.predict_duration(task_data)
# #                     except Exception as e:
# #                         logger.error(f"Prediction failed for task {i+1}: {str(e)}", exc_info=True)
# #                         raise ValueError(f"Could not generate prediction for task {i+1}. Please try again.")

# #                     # Format prediction result
# #                     hours = int(predicted_minutes // 60)
# #                     minutes = int(predicted_minutes % 60)
# #                     prediction_text = f"{hours} hours {minutes} minutes"

# #                     predictions.append({
# #                         "name": task_name,
# #                         "due_date": due_date_str,
# #                         "priority": priority,
# #                         "category": category,
# #                         "prediction": prediction_text
# #                     })
                
# #                 # Calculate total predicted time
# #                 total_predicted = sum(
# #                     int(pred['prediction'].split()[0]) * 60 + int(pred['prediction'].split()[2])
# #                     for pred in predictions
# #                 ) / 60  # in hours
                
# #                 # Add time comparison
# #                 time_comparison = ""
# #                 if time_period < total_predicted:
# #                     time_comparison = f"<p class='error'>Warning: Your available time ({time_period} hours) is less than the total predicted time ({total_predicted:.1f} hours)</p>"
# #                 else:
# #                     time_comparison = f"<p class='prediction'>Your available time ({time_period} hours) is sufficient for all tasks (total predicted: {total_predicted:.1f} hours)</p>"
                
# #                 return render_template("index.html", predictions=predictions, time_comparison=time_comparison, step=3)
            
# #             else:
# #                 # This is the old single-task form
# #                 task_name = request.form.get("task_name", "").strip()
# #                 due_date_str = request.form.get("due_date", "")
# #                 priority = request.form.get("priority", "").lower()
# #                 category = request.form.get("category", "").lower()

# #                 # Basic validation
# #                 if not task_name:
# #                     raise ValueError("Task name is required")
# #                 if not due_date_str:
# #                     raise ValueError("Due date is required")
# #                 if not priority:
# #                     raise ValueError("Priority is required")
# #                 if not category:
# #                     raise ValueError("Category is required")

# #                 # Parse and validate due date
# #                 try:
# #                     due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
# #                     if due_date < datetime.today():
# #                         raise ValueError("Due date cannot be in the past")
# #                 except ValueError as e:
# #                     raise ValueError("Invalid date format. Please use YYYY-MM-DD") from e

# #                 # Calculate urgency using Task's PRIORITY_MAP
# #                 days_until_due = (due_date - datetime.today()).days
# #                 days_until_due = max(days_until_due, 1)  # Prevent division by zero
# #                 urgency = Task.PRIORITY_MAP[priority] / (days_until_due + Task.PRIORITY_MAP[priority])

# #                 # Prepare task data for prediction
# #                 task_data = {
# #                     "priority": priority,
# #                     "category": category,
# #                     "urgency": urgency
# #                 }

# #                 # Make prediction
# #                 try:
# #                     predicted_minutes = predictor.predict_duration(task_data)
# #                 except Exception as e:
# #                     logger.error(f"Prediction failed: {str(e)}", exc_info=True)
# #                     raise ValueError("Could not generate prediction. Please try again.")

# #                 # Format prediction result
# #                 hours = int(predicted_minutes // 60)
# #                 minutes = int(predicted_minutes % 60)
# #                 prediction_text = (f"Predicted duration for '{task_name}': "
# #                                 f"{hours} hours {minutes} minutes")

# #                 # For single task, wrap it in a predictions array to match the template
# #                 predictions = [{
# #                     "name": task_name,
# #                     "due_date": due_date_str,
# #                     "priority": priority,
# #                     "category": category,
# #                     "prediction": prediction_text
# #                 }]
                
# #                 return render_template("index.html", predictions=predictions, step=3)

# #         except ValueError as e:
# #             logger.warning(f"Validation error: {str(e)}")
# #             return render_template("index.html", error=str(e), step=2 if 'total_tasks' in request.form else 1)
# #         except Exception as e:
# #             logger.error(f"Unexpected error: {str(e)}", exc_info=True)
# #             return render_template("index.html", error="An unexpected error occurred. Please try again.", step=2 if 'total_tasks' in request.form else 1)

# #     # GET request - show initial form
# #     return render_template("index.html", step=1)

# # if __name__ == "__main__":
# #     from waitress import serve
# #     logger.info("Starting TaskMate server on port 5001...")
# #     serve(app, host="0.0.0.0", port=5001)



# from flask import Flask, request, render_template
# from datetime import datetime, timedelta
# from TaskDurationPredictor import TaskDurationPredictor
# from task import Task  # Import Task to access PRIORITY_MAP
# from Scheduling import Scheduler
# import logging

# app = Flask(__name__)

# # Initialize the predictor
# predictor = TaskDurationPredictor()

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Ensure model is trained at startup
# if not hasattr(predictor.model, 'estimators_'):
#     logger.info("Initializing model...")
#     try:
#         if predictor.train():
#             logger.info("Model trained successfully")
#         else:
#             logger.error("Model training failed - predictions will not work")
#     except Exception as e:
#         logger.error(f"Model initialization failed: {str(e)}")

# # Custom template filters
# @app.template_filter('timeformat')
# def timeformat(value, format='%H:%M'):
#     return value.strftime(format)

# @app.template_filter('timedeltaformat')
# def timedeltaformat(value):
#     total_seconds = value.total_seconds()
#     hours = int(total_seconds // 3600)
#     minutes = int((total_seconds % 3600) // 60)
#     return f"{hours}h {minutes}m"

# @app.route("/", methods=["GET", "POST"])
# def home():
#     if request.method == "POST":
#         try:
#             # Check if this is the initial form or task submission
#             if 'total_tasks' in request.form:
#                 # This is the multi-task submission
#                 total_tasks = int(request.form.get("total_tasks", 0))
#                 time_period = float(request.form.get("time_period", 0))
                
#                 if total_tasks <= 0:
#                     raise ValueError("Number of tasks must be at least 1")
#                 if time_period <= 0:
#                     raise ValueError("Time period must be positive")
                
#                 tasks = []
#                 predictions = []
                
#                 for i in range(total_tasks):
#                     # Get and validate form data for each task
#                     task_name = request.form.get(f"task_name_{i}", "").strip()
#                     due_date_str = request.form.get(f"due_date_{i}", "")
#                     priority = request.form.get(f"priority_{i}", "").lower()
#                     category = request.form.get(f"category_{i}", "").lower()

#                     # Basic validation
#                     if not task_name:
#                         raise ValueError(f"Task name is required for task {i+1}")
#                     if not due_date_str:
#                         raise ValueError(f"Due date is required for task {i+1}")
#                     if not priority:
#                         raise ValueError(f"Priority is required for task {i+1}")
#                     if not category:
#                         raise ValueError(f"Category is required for task {i+1}")

#                     # Parse and validate due date
#                     try:
#                         due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
#                         if due_date < datetime.today():
#                             raise ValueError(f"Due date cannot be in the past for task {i+1}")
#                     except ValueError as e:
#                         raise ValueError(f"Invalid date format for task {i+1}. Please use YYYY-MM-DD") from e

#                     # Calculate urgency using Task's PRIORITY_MAP
#                     days_until_due = (due_date - datetime.today()).days
#                     days_until_due = max(days_until_due, 1)  # Prevent division by zero
#                     urgency = Task.PRIORITY_MAP[priority] / (days_until_due + Task.PRIORITY_MAP[priority])

#                     # Prepare task data for prediction
#                     task_data = {
#                         "priority": priority,
#                         "category": category,
#                         "urgency": urgency
#                     }

#                     # Make prediction
#                     try:
#                         predicted_minutes = predictor.predict_duration(task_data)
#                     except Exception as e:
#                         logger.error(f"Prediction failed for task {i+1}: {str(e)}", exc_info=True)
#                         raise ValueError(f"Could not generate prediction for task {i+1}. Please try again.")

#                     # Format prediction result
#                     hours = int(predicted_minutes // 60)
#                     minutes = int(predicted_minutes % 60)
#                     prediction_text = f"{hours} hours {minutes} minutes"

#                     # Create Task object for scheduling
#                     task_obj = Task(
#                         name=task_name,
#                         due_date=due_date,
#                         priority=priority,
#                         category=category,
#                         time=timedelta(minutes=predicted_minutes)
#                     )
#                     tasks.append(task_obj)

#                     predictions.append({
#                         "name": task_name,
#                         "due_date": due_date_str,
#                         "priority": priority,
#                         "category": category,
#                         "prediction": prediction_text,
#                         "urgency": urgency
#                     })
                
#                 # Schedule the tasks
#                 start_time = datetime.now()
#                 end_time = start_time + timedelta(hours=time_period)
#                 scheduler = Scheduler(tasks, start_time, end_time)
#                 completed_tasks, incomplete_tasks = scheduler.calculate_amount_of_time()

#                 # Calculate total predicted time
#                 total_predicted = sum(
#                     task.time.total_seconds() / 3600
#                     for task in tasks
#                 )
                
#                 # Add time comparison
#                 time_comparison = ""
#                 if time_period < total_predicted:
#                     time_comparison = f"<p class='error'>Warning: Your available time ({time_period:.1f} hours) is less than the total predicted time ({total_predicted:.1f} hours)</p>"
#                 else:
#                     time_comparison = f"<p class='prediction'>Your available time ({time_period:.1f} hours) is sufficient for all tasks (total predicted: {total_predicted:.1f} hours)</p>"
                
#                 return render_template("index.html", 
#                                     predictions=predictions,
#                                     time_comparison=time_comparison,
#                                     step=3,
#                                     completed_tasks=completed_tasks,
#                                     incomplete_tasks=incomplete_tasks,
#                                     start_time=start_time)
            
#             else:
#                 # This is the old single-task form (keep for backward compatibility)
#                 task_name = request.form.get("task_name", "").strip()
#                 due_date_str = request.form.get("due_date", "")
#                 priority = request.form.get("priority", "").lower()
#                 category = request.form.get("category", "").lower()

#                 # Basic validation
#                 if not task_name:
#                     raise ValueError("Task name is required")
#                 if not due_date_str:
#                     raise ValueError("Due date is required")
#                 if not priority:
#                     raise ValueError("Priority is required")
#                 if not category:
#                     raise ValueError("Category is required")

#                 # Parse and validate due date
#                 try:
#                     due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
#                     if due_date < datetime.today():
#                         raise ValueError("Due date cannot be in the past")
#                 except ValueError as e:
#                     raise ValueError("Invalid date format. Please use YYYY-MM-DD") from e

#                 # Calculate urgency using Task's PRIORITY_MAP
#                 days_until_due = (due_date - datetime.today()).days
#                 days_until_due = max(days_until_due, 1)  # Prevent division by zero
#                 urgency = Task.PRIORITY_MAP[priority] / (days_until_due + Task.PRIORITY_MAP[priority])

#                 # Prepare task data for prediction
#                 task_data = {
#                     "priority": priority,
#                     "category": category,
#                     "urgency": urgency
#                 }

#                 # Make prediction
#                 try:
#                     predicted_minutes = predictor.predict_duration(task_data)
#                 except Exception as e:
#                     logger.error(f"Prediction failed: {str(e)}", exc_info=True)
#                     raise ValueError("Could not generate prediction. Please try again.")

#                 # Format prediction result
#                 hours = int(predicted_minutes // 60)
#                 minutes = int(predicted_minutes % 60)
#                 prediction_text = (f"Predicted duration for '{task_name}': "
#                                 f"{hours} hours {minutes} minutes")

#                 # For single task, wrap it in a predictions array to match the template
#                 predictions = [{
#                     "name": task_name,
#                     "due_date": due_date_str,
#                     "priority": priority,
#                     "category": category,
#                     "prediction": prediction_text,
#                     "urgency": urgency
#                 }]
                
#                 return render_template("index.html", predictions=predictions, step=3)

#         except ValueError as e:
#             logger.warning(f"Validation error: {str(e)}")
#             return render_template("index.html", error=str(e), step=2 if 'total_tasks' in request.form else 1)
#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}", exc_info=True)
#             return render_template("index.html", error="An unexpected error occurred. Please try again.", step=2 if 'total_tasks' in request.form else 1)

#     # GET request - show initial form
#     return render_template("index.html", step=1)

# if __name__ == "__main__":
#     from waitress import serve
#     logger.info("Starting TaskMate server on port 5001...")
#     serve(app, host="0.0.0.0", port=5001)


from flask import Flask, request, render_template
from datetime import datetime, timedelta
from TaskDurationPredictor import TaskDurationPredictor
import logging

app = Flask(__name__)
predictor = TaskDurationPredictor()

class Task:
    PRIORITY_WEIGHTS = {'low': 1, 'medium': 2, 'high': 3}
    
    def __init__(self, name, priority, category, duration):
        self.name = name
        self.priority = priority
        self.category = category
        self.duration = duration  # in minutes
        self.weight = self.PRIORITY_WEIGHTS[priority]

class DayScheduler:
    def __init__(self, tasks, available_hours):
        self.tasks = sorted(tasks, key=lambda x: x.weight, reverse=True)
        self.available_minutes = available_hours * 60
        
    def create_schedule(self):
        scheduled = []
        remaining_time = self.available_minutes
        current_time = datetime.now().replace(hour=9, minute=0)  # Start at 9 AM
        
        for task in self.tasks:
            if task.duration <= remaining_time:
                end_time = current_time + timedelta(minutes=task.duration)
                scheduled.append({
                    'name': task.name,
                    'start': current_time.strftime("%H:%M"),
                    'end': end_time.strftime("%H:%M"),
                    'duration': f"{int(task.duration)} mins",
                    'priority': task.priority.capitalize(),
                    'category': task.category.capitalize()
                })
                current_time = end_time
                remaining_time -= task.duration
        
        return {
            'scheduled_tasks': scheduled,
            'remaining_time': remaining_time
        }

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            total_tasks = int(request.form.get("total_tasks", 1))
            available_hours = float(request.form.get("time_period", 8))
            
            tasks = []
            for i in range(total_tasks):
                # Prepare input for your existing predictor
                task_input = {
                    'priority': request.form.get(f"priority_{i}"),
                    'category': request.form.get(f"category_{i}"),
                    'urgency': 0.5  # Default value since no dates
                }
                
                # Get prediction using your UNMODIFIED predictor
                duration = predictor.predict_duration(task_input)
                
                tasks.append(Task(
                    name=request.form.get(f"task_name_{i}").strip(),
                    priority=task_input['priority'],
                    category=task_input['category'],
                    duration=duration
                ))

            scheduler = DayScheduler(tasks, available_hours)
            schedule = scheduler.create_schedule()
            
            return render_template("index.html", 
                                schedule=schedule,
                                available_hours=available_hours,
                                step=3)
            
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return render_template("index.html", 
                                error=str(e),
                                step=2)

    return render_template("index.html", step=1)

if __name__ == "__main__":
    app.run(debug=True)