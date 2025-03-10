import pandas as pd
import joblib
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
        df["priority"] = df["priority"].map({"low": 1, "medium": 2, "high": 3})
        df["category"] = df["category"].astype("category").cat.codes  # Convert category to numbers
        return df

    def train(self, csv_filename="tasks.csv"):
        """Train the model on existing data."""
        df = self.load_data(csv_filename)
        
        # Features and target
        X = df[["priority", "category", "urgency"]]
        y = df["duration"]
        
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
        
        task_data = [[
            {"low": 1, "medium": 2, "high": 3}[task.priority],  # Convert priority
            task.category,  # Assuming it's already an int
            task.urgency
        ]]
        
        return self.model.predict(task_data)[0]
