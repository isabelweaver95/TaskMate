from datetime import datetime, timedelta
import pandas as pd
import joblib
from task import Task
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

class TaskDurationPredictor:
    def __init__(self, model_filename="task_model.pkl"):
        self.model_filename = model_filename
        self.model = RandomForestRegressor()

    def load_data(self, csv_filename="tasks.csv"):
        """Load and preprocess the dataset."""
        df = pd.read_csv(csv_filename)
        
        # Map priority to numeric values
        df["priority"] = df["priority"].map({"low": 1, "medium": 2, "high": 3})
        
        # Convert category to numeric codes
        df["category"] = df["category"].astype("category").cat.codes
        
        return df

    def train(self, csv_filename="tasks.csv", extra_param=None):
        """Train the model on existing data."""
        df = self.load_data(csv_filename)
        
        # Features (X) and target (y)
        X = df[["priority", "category", "urgency"]]  # Features
        y = df["duration"]  # Target variable (duration)
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        predictions = self.model.predict(X_test)
        print("Model Trained - MAE:", mean_absolute_error(y_test, predictions))

        # Save the trained model
        joblib.dump(self.model, self.model_filename)

    def predict_duration(self, task):
        """Predict the duration of a new task."""
        if not self.model:
            self.model = joblib.load(self.model_filename)  # Load the model if not already loaded
        
        # Create a mapping for categories (same as during training)
        category_mapping = {"hobby": 0, "household": 1}  # Update this based on your data
        
        # Map task attributes to model features
        task_data = [[
            Task.PRIORITY_MAP[task.priority],  # Convert priority to numeric value
            category_mapping.get(task.category, -1),  # Convert category to numeric code
            task.urgency  # Use calculated urgency
        ]]
        
        # Predict duration
        return self.model.predict(task_data)[0]



# # Train the model
# predictor = TaskDurationPredictor()
# predictor.train("tasks.csv")

# # Compare predictions with actual values
# df = predictor.load_data("tasks.csv")
# X = df[["priority", "category", "urgency"]]
# y = df["duration"]
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# predictions = predictor.model.predict(X_test)
# for i in range(len(X_test)):
#     print(f"Actual: {y_test.iloc[i]}, Predicted: {predictions[i]}")

# Plot actual vs. predicted durations
# plt.scatter(y_test, predictions)
# plt.xlabel("Actual Duration")
# plt.ylabel("Predicted Duration")
# plt.title("Actual vs. Predicted Durations")
# plt.show()

# # Plot feature importance
# importances = predictor.model.feature_importances_
# feature_names = ["priority", "category", "urgency"]
# plt.bar(feature_names, importances)
# plt.xlabel("Features")
# plt.ylabel("Importance")
# plt.title("Feature Importance")
# plt.show()

# Test with a new task
# new_task = Task(
#     name="Laundry",
#     time=5,  # Duration in hours (not used in prediction)
#     due_date="2025-03-17",  # Due date in YYYY-MM-DD format
#     priority="high",
#     category="hobby"  # Example category
# )
# predicted_duration = predictor.predict_duration(new_task)
# print("Predicted Duration:", predicted_duration)