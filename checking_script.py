import pandas as pd

# Read the CSV file
data = pd.read_csv("comedia_full.csv")

# Extract the relevant column (assuming Violence Rings is the 25th column, index 24)
values = data.iloc[5:73, 18].tolist()

# Identify non-numeric values
non_numeric_values = [val for val in values if pd.isna(pd.to_numeric(str(val).strip(), errors='coerce'))]

# Print non-numeric values
print("Non-Numeric Values:", non_numeric_values)