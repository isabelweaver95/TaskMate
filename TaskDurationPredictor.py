from datetime import datetime, timedelta
import pandas as pd
import joblib
from task import Task
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

class TaskDurationPredictor:    
    def __init__(self, model_filename="task_model.pkl"):
        self.model_filename = model_filename
        self.model = RandomForestRegressor()
        self.priority_map = {'low': 1, 'medium': 2, 'high': 3}
        self.category_mapping = {
            'hobby': 0,
            'household': 1,
            'health': 2,
            'education': 3,
            'personal': 4
        }

    def load_data(self, csv_filename="tasks.csv"):
        """Load and clean data"""
        df = pd.read_csv(csv_filename)
        
        # ===== DATA CLEANING =====
        # 1. Convert all strings to lowercase and strip whitespace
        string_cols = ['priority', 'category']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().str.strip()
        
        # 2. Clean numeric columns
        numeric_cols = ['urgency', 'duration']
        for col in numeric_cols:
            if col in df.columns:
                # Convert to numeric, coercing errors to NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaN with defaults (urgency: 0.5, duration: median)
                default = 0.5 if col == 'urgency' else df[col].median()
                df[col] = df[col].fillna(default)
        
        # 3. Validate required columns
        required_cols = ['priority', 'category', 'urgency', 'duration']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")
        
        # 4. Validate priority values
        valid_priorities = ['low', 'medium', 'high']
        invalid_pri = df[~df['priority'].isin(valid_priorities)]
        if not invalid_pri.empty:
            print(f"Warning: Found invalid priorities: {invalid_pri['priority'].unique()}")
            df['priority'] = df['priority'].replace(
                [x for x in invalid_pri['priority'].unique() if x not in valid_priorities],
                'medium'  # Default to medium
            )
        
        return df

    def train(self, csv_filename="tasks.csv"):
        """Enhanced training with better validation"""
        try:
            df = self.load_data(csv_filename)
            
            # 1. Verify we have enough data
            if len(df) < 10:
                raise ValueError(f"Only {len(df)} samples - need at least 10 for meaningful training")
            
            # 2. Enhanced feature engineering
            df['priority'] = df['priority'].str.lower().map(self.priority_map).fillna(2)
            df['category'] = df['category'].str.lower().map(self.category_mapping).fillna(-1)
            df['urgency'] = pd.to_numeric(df['urgency'], errors='coerce').fillna(0.5)
            
            # 3. Verify feature ranges
            print("\n==== Feature Verification ====")
            print("Priority values:", df['priority'].unique())
            print("Category values:", df['category'].unique())
            print("Urgency range:", df['urgency'].min(), "to", df['urgency'].max())
            print("Duration range:", df['duration'].min(), "to", df['duration'].max())
            
            # 4. Train with more trees and depth
            self.model = RandomForestRegressor(
                n_estimators=100,  # Increased from default 10
                max_depth=5,       # Prevent overfitting
                random_state=42
            )
            
            X = df[["priority", "category", "urgency"]]
            y = df["duration"]
            
            self.model.fit(X, y)
            
            # 5. Feature importance check
            print("\n==== Feature Importance ====")
            for name, importance in zip(X.columns, self.model.feature_importances_):
                print(f"{name}: {importance:.2f}")
            
            # Save model
            joblib.dump({
                'model': self.model,
                'category_mapping': self.category_mapping,
                'priority_map': self.priority_map
            }, self.model_filename)
            
            print("\n\033[92mTraining successful!\033[0m")
            return True
            
        except Exception as e:
            print(f"\n\033[91mTraining failed: {str(e)}\033[0m")
            return False
        

    def predict_duration(self, task):
        """Enhanced prediction with debugging"""
        try:
            # Debug input
            print("\n==== Prediction Input ====")
            print("Raw input:", task)
            
            # Load model if needed
            if not hasattr(self.model, 'estimators_'):
                saved = joblib.load(self.model_filename)
                self.model = saved['model']
                self.category_mapping = saved['category_mapping']
                self.priority_map = saved['priority_map']
            
            # Prepare features with validation
            priority = str(task.get('priority', 'medium')).lower()
            category = str(task.get('category', '')).lower()
            urgency = float(task.get('urgency', 0.5))
            
            features = [
                self.priority_map.get(priority, 2),  # default medium
                self.category_mapping.get(category, -1),  # unknown
                max(0, min(1, urgency))  # clamp to 0-1 range
            ]
            
            print("Processed features:", features)
            
            # Predict and ensure reasonable output
            prediction = max(1, min(240, self.model.predict([features])[0]))  # 1min to 4hrs
            print("Raw prediction:", prediction)
            
            return prediction
            
        except Exception as e:
            print(f"\n\033[91mPrediction error: {str(e)}\033[0m")
            return 30  # Fallback value
        
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

    def print_predictions(self, csv_filename="tasks.csv"):
        """Print actual vs predicted durations in terminal"""
        try:
            df = self.load_data(csv_filename)
            
            # Prepare features
            df['priority'] = df['priority'].map(self.priority_map)
            df['category'] = df['category'].map(self.category_mapping)
            X = df[["priority", "category", "urgency"]]
            y_true = df["duration"]
            
            # Make predictions
            y_pred = self.model.predict(X)
            
            # Print header
            print("\n" + "="*70)
            print(f"{'Task Name':<20} | {'Actual':>7} | {'Predicted':>9} | {'Difference':>10}")
            print("-"*70)
            
            # Print each prediction
            for i, (true, pred) in enumerate(zip(y_true, y_pred)):
                task_name = df.iloc[i].get('name', f'Task {i+1}')[:18] + ("..." if len(df.iloc[i].get('name', '')) > 18 else "")
                diff = pred - true
                diff_str = f"{diff:+.1f}"
                
                # Color coding
                if abs(diff) < 5:
                    diff_str = f"\033[92m{diff_str}\033[0m"  # Green
                elif abs(diff) < 15:
                    diff_str = f"\033[93m{diff_str}\033[0m"  # Yellow
                else:
                    diff_str = f"\033[91m{diff_str}\033[0m"  # Red
                    
                print(f"{task_name:<20} | {true:>7.1f} | {pred:>9.1f} | {diff_str:>10}")
            
            # Print summary stats
            mae = (y_pred - y_true).abs().mean()
            print("="*70)
            print(f"Mean Absolute Error: \033[1m{mae:.2f} minutes\033[0m")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n\033[91mError displaying predictions: {str(e)}\033[0m\n")

# from datetime import datetime, timedelta
# import pandas as pd
# import joblib
# import matplotlib.pyplot as plt
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_absolute_error, r2_score, median_absolute_error
# import numpy as np
# import warnings

# class EnhancedTaskDurationPredictor:    
#     def __init__(self, model_filename="enhanced_task_model.pkl"):
#         self.model_filename = model_filename
#         self.model = None
#         self.priority_map = {'low': 1, 'medium': 2, 'high': 3}
#         self.category_mapping = {
#             'hobby': 0,
#             'household': 1,
#             'health': 2,
#             'education': 3,
#             'personal': 4
#         }
#         self.log_transform = True  # Initialize the attribute here
#         self.feature_names = ['priority_encoded', 'category_encoded', 'urgency', 'interaction']

#     def load_data(self, csv_filename="tasks.csv"):
#         """Enhanced data loading with feature engineering"""
#         try:
#             df = pd.read_csv(csv_filename)
            
#             # === Data Cleaning ===
#             # Handle missing values
#             df = df.dropna(subset=['duration'])
            
#             # Clean categorical features
#             df['priority'] = (df['priority']
#                              .astype(str)
#                              .str.lower()
#                              .str.strip()
#                              .apply(lambda x: x if x in self.priority_map else 'medium'))
            
#             df['category'] = (df['category']
#                              .astype(str)
#                              .str.lower()
#                              .str.strip()
#                              .apply(lambda x: x if x in self.category_mapping else 'personal'))
            
#             # Clean and clip numeric features
#             df['urgency'] = pd.to_numeric(df['urgency'], errors='coerce').clip(0, 1).fillna(0.5)
#             df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
#             df = df[df['duration'] > 0]  # Remove invalid durations
            
#             # === Feature Engineering ===
#             df['log_duration'] = np.log1p(df['duration'])
#             df['priority_encoded'] = df['priority'].map(self.priority_map)
#             df['category_encoded'] = df['category'].map(self.category_mapping)
#             df['interaction'] = df['urgency'] * df['priority_encoded']
            
#             # Validate final dataset
#             if len(df) < 50:
#                 raise ValueError(f"Insufficient data: only {len(df)} valid samples")
                
#             return df
            
#         except Exception as e:
#             print(f"\033[91mData loading failed: {str(e)}\033[0m")
#             raise

#     def train(self, csv_filename="tasks.csv", test_size=0.2):
#         """Enhanced training with feature engineering"""
#         try:
#             df = self.load_data(csv_filename)
            
#             # Prepare features
#             X = df[self.feature_names]
#             y = df['log_duration'] if self.log_transform else df['duration']
            
#             # Train-test split
#             X_train, X_test, y_train, y_test = train_test_split(
#                 X, y, test_size=test_size, random_state=42
#             )
            
#             # Optimized model
#             self.model = RandomForestRegressor(
#                 n_estimators=300,
#                 max_depth=12,
#                 min_samples_leaf=5,
#                 max_features=0.8,
#                 random_state=42,
#                 n_jobs=-1
#             )
#             self.model.fit(X_train, y_train)
            
#             # Evaluate
#             y_pred = self.model.predict(X_test)
            
#             # Convert back from log scale if needed
#             if self.log_transform:
#                 y_test = np.expm1(y_test)
#                 y_pred = np.expm1(y_pred)
            
#             mae = mean_absolute_error(y_test, y_pred)
#             medae = median_absolute_error(y_test, y_pred)
#             r2 = r2_score(y_test, y_pred)
            
#             print("\n\033[1m=== Enhanced Training Report ===\033[0m")
#             print(f"MAE: {mae:.2f} minutes")
#             print(f"Median AE: {medae:.2f} minutes")
#             print(f"R² Score: {r2:.2f}")
#             print("\nFeature Importances:")
#             for feat, imp in zip(self.feature_names, self.model.feature_importances_):
#                 print(f"  {feat}: {imp:.2f}")
            
#             # Save model with metadata
#             joblib.dump({
#                 'model': self.model,
#                 'mappings': {
#                     'priority': self.priority_map,
#                     'category': self.category_mapping
#                 },
#                 'log_transform': self.log_transform,
#                 'feature_names': self.feature_names
#             }, self.model_filename)
            
#             return True
            
#         except Exception as e:
#             print(f"\033[91mTraining failed: {str(e)}\033[0m")
#             return False

#     def predict_duration(self, task):
#         """Robust prediction with post-processing"""
#         try:
#             # Load model if needed
#             if self.model is None:
#                 saved = joblib.load(self.model_filename)
#                 self.model = saved['model']
#                 self.priority_map = saved['mappings']['priority']
#                 self.category_mapping = saved['mappings']['category']
#                 self.log_transform = saved.get('log_transform', True)
#                 self.feature_names = saved.get('feature_names', 
#                     ['priority_encoded', 'category_encoded', 'urgency', 'interaction'])
            
#             # Prepare input features
#             priority = str(task.get('priority', 'medium')).lower()
#             category = str(task.get('category', 'personal')).lower()
#             urgency = float(task.get('urgency', 0.5))
            
#             features = np.array([[
#                 self.priority_map.get(priority, 2),  # priority_encoded
#                 self.category_mapping.get(category, 4),  # category_encoded
#                 np.clip(urgency, 0, 1),  # urgency
#                 self.priority_map.get(priority, 2) * np.clip(urgency, 0, 1)  # interaction
#             ]])
            
#             # Predict
#             with warnings.catch_warnings():
#                 warnings.simplefilter("ignore")
#                 prediction = self.model.predict(features)[0]
                
#             # Convert back from log if needed
#             if self.log_transform:
#                 prediction = np.expm1(prediction)
            
#             # Post-processing rules
#             prediction = max(1, min(prediction, 480))  # 1min to 8hrs
            
#             # Boost short high-priority tasks
#             if prediction < 20 and priority == 'high':
#                 prediction *= 1.5
                
#             return round(prediction, 1)
            
#         except Exception as e:
#             print(f"\033[91mPrediction error: {str(e)}\033[0m")
#             return None

#     def evaluate_model(self, csv_filename="tasks.csv"):
#         """Comprehensive evaluation with visualizations"""
#         try:
#             df = self.load_data(csv_filename)
            
#             # Prepare features
#             X = df[self.feature_names]
            
#             if self.log_transform:
#                 y_true = np.expm1(df['log_duration'])
#             else:
#                 y_true = df['duration']
            
#             # Predict
#             y_pred = self.predict_batch(X)
            
#             # Generate report
#             errors = np.abs(y_pred - y_true)
#             results = pd.DataFrame({
#                 'Actual': y_true,
#                 'Predicted': y_pred,
#                 'Error': errors
#             })
            
#             print("\n\033[1m=== Enhanced Evaluation Report ===\033[0m")
#             print(results.describe())
            
#             # Error distribution
#             print("\nError Percentiles (minutes):")
#             print(f"50th: {np.percentile(errors, 50):.1f}")
#             print(f"75th: {np.percentile(errors, 75):.1f}")
#             print(f"90th: {np.percentile(errors, 90):.1f}")
#             print(f"Critical Errors (>60min): {(errors > 60).mean():.1%}")
            
#             # Plot
#             plt.figure(figsize=(12, 6))
#             plt.scatter(y_true, y_pred, alpha=0.3)
#             plt.plot([y_true.min(), y_true.max()], 
#                     [y_true.min(), y_true.max()], 'r--')
#             plt.xlabel('Actual Duration (minutes)')
#             plt.ylabel('Predicted Duration (minutes)')
#             plt.title('Actual vs Predicted Durations')
#             plt.show()
            
#             return results
            
#         except Exception as e:
#             print(f"\033[91mEvaluation failed: {str(e)}\033[0m")
#             return None

#     def predict_batch(self, X):
#         """Batch prediction for evaluation"""
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")
#             preds = self.model.predict(X)
        
#         if self.log_transform:
#             return np.expm1(preds)
#         return preds

# if __name__ == "__main__":
#     print("=== Enhanced Task Duration Predictor ===")
#     predictor = EnhancedTaskDurationPredictor()
    
#     # Train
#     print("\nTraining model...")
#     predictor.train("tasks.csv")
    
#     # Test prediction
#     test_task = {
#         'priority': 'high',
#         'category': 'education',
#         'urgency': 0.9
#     }
#     print(f"\nPrediction for {test_task}:")
#     print(f"{predictor.predict_duration(test_task)} minutes")
    
#     # Evaluate
#     print("\nEvaluating model...")
#     predictor.evaluate_model()