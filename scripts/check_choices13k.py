from pathlib import Path
import pandas as pd
import json

selections_path = Path("data/raw/choices13k/c13k_selections.csv")
problems_path = Path("data/raw/choices13k/c13k_problems.json")

print("Checking files...")
print(f"Selections exists: {selections_path.exists()}")
print(f"Problems exists: {problems_path.exists()}")

print("\nLoading selections...")
df = pd.read_csv(selections_path)
print(df.shape)
print(df.head())
print("\nColumns:")
print(list(df.columns))

print("\nLoading problems...")
with open(problems_path, "r", encoding="utf-8") as f:
    problems = json.load(f)

print(type(problems))
print(f"Number of problems: {len(problems)}")

first_key = list(problems.keys())[0]
print("\nFirst problem key:")
print(first_key)

print("\nFirst problem content:")
print(problems[first_key])

