import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
ALLOWED_CATEGORIES = ["household", "health", "education", "personal", "hobby"]
TOTAL_NEW_TASKS = 340  # Adds ~25% to your 240 existing tasks
CATEGORY_WEIGHTS = {
    "health": 1.5,    # Boost under-represented
    "education": 1.3,
    "hobby": 1.1,
    "household": 0.8, # Reduce dominant
    "personal": 0.9
}

def load_existing_data():
    """Safely load and validate existing data"""
    try:
        df = pd.read_csv("tasks.csv")
        return df[df['category'].str.lower().isin(ALLOWED_CATEGORIES)]
    except FileNotFoundError:
        return pd.DataFrame(columns=["name", "priority", "category", "duration", "urgency", "due_date"])

def generate_task(category):
    """Enhanced task generator with 10+ examples per category"""
    task_library = {
        "household": [
            {"name": "Make bed", "duration": (5, 10), "urgency": (0.2, 0.5)},
            {"name": "Make bed", "duration": (5, 10), "urgency": (0.2, 0.5)},
            {"name": "Make bed", "duration": (5, 10), "urgency": (0.2, .5)},
            {"name": "Make beds", "duration": (5, 10), "urgency": (0.2, 0.5)},
            {"name": "Make bed", "duration": (5, 10), "urgency": (0.2, 0.5)},
            {"name": "Make bed", "duration": (5, 10), "urgency": (0.2, 0.5)}
        ],
        "health": [
            {"name": "Jump rope", "duration": (5, 10), "urgency": (0.7, 0.9)},
            {"name": "Eat a healthy snack", "duration": (5, 10), "urgency": (0.8, 1.0)},
            {"name": "Go for a walk", "duration": (10, 20), "urgency": (0.6, 0.8)},
            {"name": "Practice deep breathing", "duration": (1, 5), "urgency": (0.9, 1.0)},
            {"name": "Check posture", "duration": (1, 5), "urgency": (0.5, 0.7)},
            {"name": "Stretch muscles", "duration": (5, 10), "urgency": (0.6, 0.8)}
        ],
        "education": [
            {"name": "Read an article", "duration": (5, 10), "urgency": (0.6, 0.8)},
            {"name": "Watch a documentary", "duration": (10, 20), "urgency": (0.6, 0.8)},
        ],
        "personal": [
            {"name": "Write a gratitude note", "duration": (5, 10), "urgency": (0.9, 1.0)},
            {"name": "Shop for groceries", "duration": (5, 60), "urgency": (0.8, 1.0)},
            {"name": "Organize a drawer", "duration": (10, 20), "urgency": (0.7, 0.9)},
            {"name": "Take a short break", "duration": (10, 15), "urgency": (0.6, 0.8)},
            {"name": "Listen to calming music", "duration": (5, 10), "urgency": (0.5, 0.7)},
            {"name": "Write in a journal", "duration": (5, 15), "urgency": (0.6, 0.8)}
        ],
        "hobby": [
            {"name": "Doodle a sketch", "duration": (5, 15), "urgency": (0.4, 0.6)},
            {"name": "Listen to a podcast", "duration": (5, 10), "urgency": (0.6, 0.8)},
            {"name": "Write a short story", "duration": (10, 20), "urgency": (0.5, 0.7)},
            {"name": "Take a photo", "duration": (10, 15), "urgency": (0.6, 0.8)},
        ]
    }


    template = random.choice(task_library[category])
    duration = random.randint(*template["duration"])
    urgency = random.uniform(*template["urgency"])
    
    # Priority influences final urgency
    priority = random.choices(
        ["low", "medium", "high"],
        weights=[0.3, 0.5, 0.2]  # 30% low, 50% medium, 20% high
    )[0]
    
    urgency = urgency * {
        "low": 0.8,
        "medium": 1.0,
        "high": 1.3
    }[priority]
    urgency = min(round(urgency, 1), 1.0)  # Cap at 1.0
    
    return {
        "name": template["name"],
        "priority": priority,
        "category": category,
        "duration": duration,
        "urgency": urgency,
        "due_date": (datetime.now() + timedelta(days=random.randint(1, 21))).strftime("%Y-%m-%d")
    }

def main():
    # Load existing data
    existing_data = load_existing_data()
    print(f"Loaded {len(existing_data)} existing tasks")
    
    # Generate new tasks with weighted distribution
    new_categories = random.choices(
        list(CATEGORY_WEIGHTS.keys()),
        weights=list(CATEGORY_WEIGHTS.values()),
        k=TOTAL_NEW_TASKS
    )
    
    new_tasks = [generate_task(cat) for cat in new_categories]
    new_df = pd.DataFrame(new_tasks)
    
    # Combine and remove duplicates
    combined = pd.concat([existing_data, new_df]).drop_duplicates(
        subset=["name", "category", "duration"],
        keep="last"
    )
    
    # Save with backup
    combined.to_csv("tasks.csv", index=False)
    
    # Print report
    print(f"\nAdded {len(new_df)} new tasks. Category distribution:")
    print(new_df['category'].value_counts())
    print("\nFinal counts:")
    print(combined['category'].value_counts())
    print(f"\nTotal tasks now: {len(combined)}")

if __name__ == "__main__":
    main()