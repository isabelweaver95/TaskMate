import pandas as pd
from TaskDurationPredictor import TaskDurationPredictor

predictor = TaskDurationPredictor()
df = predictor.load_data()

print("\n=== Data Summary ===")
print(df.describe())

print("\n=== Value Counts ===")
print("Priorities:\n", df['priority'].value_counts())
print("\nCategories:\n", df['category'].value_counts())

print("\n=== Sample Durations ===")
print(df[['priority', 'category', 'duration']].head(10))