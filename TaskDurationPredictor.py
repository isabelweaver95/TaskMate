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
        self.category_mapping = {
            'hobby': 0,
            'household': 1,
            'health': 2,
            'education': 3,
            'personal': 4
        }

    def load_data(self, csv_filename="tasks.csv"):
        """Load data without preprocessing (we'll handle that in train())"""
        return pd.read_csv(csv_filename)

    def train(self, csv_filename="tasks.csv", extra_param=None):
        """Train the model with proper feature encoding"""
        df = self.load_data(csv_filename)
        
        # 1. Clean and standardize data
        df['priority'] = df['priority'].astype(str).str.lower()
        df['category'] = df['category'].astype(str).str.lower()
        
        # 2. Encode priority
        df['priority'] = df['priority'].map(self.priority_map)
        
        # 3. Encode categories and store the encoder
        categories = df['category'].unique()
        self.category_encoder = {cat: idx for idx, cat in enumerate(categories)}
        df['category'] = df['category'].map(self.category_encoder)
        
        # 4. Prepare features and target
        X = df[["priority", "category", "urgency"]]
        y = df["duration"]
        
        # 5. Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 6. Train model
        self.model.fit(X_train, y_train)
        
        # 7. Evaluate
        predictions = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        print(f"Model Trained - MAE: {mae:.2f}")
        
        # 8. Save model and encoder
        joblib.dump({
            'model': self.model,
            'category_encoder': self.category_encoder,
            'priority_map': self.priority_map
        }, self.model_filename)

    def predict_duration(self, task):
        """Predict duration for task data (as dictionary)"""
        try:
            if not hasattr(self.model, 'estimators_'):
                self.model = joblib.load(self.model_filename)
            
            # Prepare features using Task's PRIORITY_MAP
            features = [
                Task.PRIORITY_MAP.get(task['priority'], 1),  # priority
                self.category_mapping.get(task['category'], -1),  # category
                float(task.get('urgency', 0))  # urgency
            ]
            
            return self.model.predict([features])[0]
            
        except Exception as e:
            raise ValueError(f"Prediction failed: {str(e)}")
    
    # Add this method to automatically update your model
    def update_model(self, new_data_file):
        """Incremental model update"""
        try:
            new_data = self.load_data(new_data_file)
            self.validate_data(new_data)
            
            # Retrain with combined data
            combined = pd.concat([self.load_data(), new_data])
            self.train(combined)
            
            print("Model updated successfully")
        except Exception as e:
            print(f"Update failed: {str(e)}")