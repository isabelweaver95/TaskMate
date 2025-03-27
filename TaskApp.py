from flask import Flask, request, render_template
from datetime import datetime
from TaskDurationPredictor import TaskDurationPredictor

app = Flask(__name__)

# Initialize the predictor
predictor = TaskDurationPredictor()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            # Get user input
            task_name = request.form["task_name"]
            due_date = request.form["due_date"]
            priority = request.form["priority"].lower()
            category = request.form["category"].lower()

            # Validate input
            if not task_name or not due_date or not priority or not category:
                raise ValueError("All fields are required.")

            if priority not in ["low", "medium", "high"]:
                raise ValueError("Priority must be 'low', 'medium', or 'high'.")

            if category not in ["household", "health", "education", "personal", "hobby"]:
                raise ValueError("Invalid category. Choose from: household, health, education, personal, hobby.")

            # Calculate urgency
            due_date = datetime.strptime(due_date, "%Y-%m-%d")
            days_until_due = (due_date - datetime.today()).days
            days_until_due = max(days_until_due, 1)  # Prevent division by zero
            urgency = {"low": 1, "medium": 2, "high": 3}[priority] / (days_until_due + {"low": 1, "medium": 2, "high": 3}[priority])

            # Create task dictionary
            task = {
                "name": task_name,
                "due_date": due_date,
                "priority": priority,
                "category": category,
                "urgency": urgency,
            }

            # Predict duration
            predicted_duration = predictor.predict_duration(task)

            # Show result
            return render_template("index.html", prediction=f"Predicted duration for '{task_name}': {predicted_duration:.2f} minutes")

        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)