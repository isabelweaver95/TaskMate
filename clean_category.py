import pandas as pd

# Define category mapping from old to new categories
CATEGORY_MAPPING = {
    # Accepted categories (no change needed)
    'household': 'household',
    'health': 'health',
    'education': 'education',
    'personal': 'personal',
    'hobby': 'hobby',
    
    # Categories to remap
    'study': 'education',
    'work': 'personal',  # or 'education' if work-related learning
    'recreation': 'hobby',
    'food': 'household',  # assuming cooking/meal prep
    'workout': 'health',
    'walk': 'health',
    'basketball': 'hobby',
    'yoga': 'health',
    'quilt': 'hobby',
    'break': 'personal'
}

def clean_categories(input_file, output_file):
    # Load data
    df = pd.read_csv(input_file)
    
    # Standardize category names (lowercase, strip whitespace)
    df['category'] = df['category'].str.lower().str.strip()
    
    # Apply category mapping
    df['category'] = df['category'].map(CATEGORY_MAPPING).fillna('personal')  # default to personal
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")
    print("\nCategory distribution after cleaning:")
    print(df['category'].value_counts())

# Usage example
clean_categories('tasks.csv', 'cleaned_tasks.csv')
