from flask import Flask, request, render_template
from datetime import datetime
from TaskDurationPredictor import TaskDurationPredictor
from task import Task  # Import Task to access PRIORITY_MAP
import logging

app = Flask(__name__)

# Initialize the predictor
predictor = TaskDurationPredictor()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            # Get and validate form data
            task_name = request.form.get("task_name", "").strip()
            due_date_str = request.form.get("due_date", "")
            priority = request.form.get("priority", "").lower()
            category = request.form.get("category", "").lower()

            # Basic validation
            if not task_name:
                raise ValueError("Task name is required")
            if not due_date_str:
                raise ValueError("Due date is required")
            if not priority:
                raise ValueError("Priority is required")
            if not category:
                raise ValueError("Category is required")

            # Parse and validate due date
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                if due_date < datetime.today():
                    raise ValueError("Due date cannot be in the past")
            except ValueError as e:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD") from e

            # Calculate urgency using Task's PRIORITY_MAP
            days_until_due = (due_date - datetime.today()).days
            days_until_due = max(days_until_due, 1)  # Prevent division by zero
            urgency = Task.PRIORITY_MAP[priority] / (days_until_due + Task.PRIORITY_MAP[priority])

            # Prepare task data for prediction
            task_data = {
                "priority": priority,
                "category": category,
                "urgency": urgency
            }

            # Make prediction
            try:
                predicted_minutes = predictor.predict_duration(task_data)
            except Exception as e:
                logger.error(f"Prediction failed: {str(e)}", exc_info=True)
                raise ValueError("Could not generate prediction. Please try again.")

            # Format prediction result
            hours = int(predicted_minutes // 60)
            minutes = int(predicted_minutes % 60)
            prediction_text = (f"Predicted duration for '{task_name}': "
                             f"{hours} hours {minutes} minutes")

            return render_template("index.html", prediction=prediction_text)

        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return render_template("index.html", error=str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return render_template("index.html", error="An unexpected error occurred. Please try again.")

    return render_template("index.html")

if __name__ == "__main__":
    from waitress import serve
    logger.info("Starting TaskMate server on port 5001...")
    serve(app, host="0.0.0.0", port=5001)