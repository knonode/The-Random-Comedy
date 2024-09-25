import pandas as pd
import json

# Read the CSV file
data = pd.read_csv("comedia_full.csv", header=None)

# Extract the level names from row 1 (index 0) and the level numbers from row 2 (index 1)
level_names = data.iloc[0, 14:50].tolist()
level_numbers = data.iloc[1, 14:50].tolist()

# Combine level names and numbers
levels = [f"{name} {num}" for name, num in zip(level_names, level_numbers)]

# Extract the elements (assuming they start from row 5)
elements = data.iloc[5:72, 1].tolist()

# Extract the shuffle counts from row 4 (index 3)
shuffle_counts = data.iloc[3, 14:50].tolist()

# Create a dictionary to store the elements and their corresponding values for each level
shuffled_data = []

for level_index, level in enumerate(levels):
    # Extract values for the current level (assuming levels start from column 15, so index 14 + level_index)
    values = data.iloc[5:72, 14 + level_index].tolist()
    
    # Convert values to numeric, setting non-numeric values to 0
    values = pd.to_numeric(pd.Series(values), errors='coerce').fillna(0).tolist()
    
    # Get the shuffle count for this level
    shuffle_count = int(shuffle_counts[level_index])
    
    # Create a dictionary for the current level
    level_data = {
        "level": level,
        "shuffle_count": shuffle_count,
        "data": [{"element": el, "value": val} for el, val in zip(elements, values)]
    }
    
    # Add the current level data to the shuffled_data list
    shuffled_data.append(level_data)

# Print the data for debugging
print("Shuffled Data:", shuffled_data)

# Save the data to a JSON file
with open("shuffled_data.json", "w") as f:
    json.dump(shuffled_data, f)

print("Data saved to shuffled_data.json")