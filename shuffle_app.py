from flask import Flask, render_template, request, jsonify, session
import json
import random
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for session management

df = pd.read_csv('comedia_full.csv', header=None)  # No header in the CSV
elements = df.iloc[5:72, 1].tolist()  # Elements from row 6 to 72, column 2 (index 1)
levels = df.iloc[0, 14:50].tolist()  # Levels from row 1 (index 0), starting from column 3 (index 2)
data_for_display = df.iloc[5:72, 14:50].values.tolist()  # Data from row 6 to 72, starting from column 2

@app.route("/spreadsheet")
def spreadsheet():
    # Load the CSV data within the function
    df = pd.read_csv('comedia_full.csv', header=None)  # No header in the CSV
    elements = df.iloc[5:72, 1].tolist()  # Elements from row 6 to 72, column 2 (index 1)
    levels = df.iloc[0, 14:50].tolist()  # Levels from row 1 (index 0), columns 14 to 50 (index 13 to 49)
    data_for_display = df.iloc[5:72, 14:50].values  # Data from row 6 to 72, columns 14 to 50

    # Convert data to strings, replace NaN with empty string
    levels = [str(level) for level in levels]
    elements = [str(element) for element in elements]
    data = [['' if pd.isna(cell) else str(cell) for cell in row] for row in data_for_display]
    
    return render_template("spreadsheet.html", levels=levels, elements=elements, data=data)

# Load the data
with open("shuffled_data.json", "r") as f:
    data = json.load(f)

# Calculate total shuffles across all levels
total_shuffles = sum(level_data.get("shuffle_count", 0) for level_data in data)
print(f"Total shuffles across all levels: {total_shuffles}")

# Define the list of bonus elements
bonus_elements = ["Helium", "Neon", "Argon", "Krypton", "Xenon", "Platinum"]

# Define the list of unique body elements (all unique elements except bonus elements)
body_elements = list(set(item["element"] for level in data for item in level["data"] if item["element"] not in bonus_elements))

# Total number of collectible elements
total_elements = len(body_elements)

print(f"Body elements: {body_elements}")
print(f"Total elements: {total_elements}")

print("Loaded data:")
for level_data in data:
    print(f"Level: {level_data['level']}, Shuffle Count: {level_data.get('shuffle_count', 'Not found')}")

@app.route("/")
def start():
    return render_template("start.html")

@app.route("/game")
def game():
    # This is your existing index route logic
    levels = [level_data["level"] for level_data in data]
    
    # Initialize the body list in the session if it doesn't exist
    if 'body' not in session:
        session['body'] = []
    
    # Initialize the shuffle counts in the session if it doesn't exist
    if 'shuffle_counts' not in session:
        session['shuffle_counts'] = {level_data["level"]: 0 for level_data in data}
    
    # Start with the first level (Dark Forest)
    initial_level_data = data[0]
    
    print(f"Rendering index with total_elements: {total_elements}")
    return render_template("index.html", 
                           levels=levels, 
                           data=data, 
                           selected_level=initial_level_data["level"], 
                           body=session.get('body', []), 
                           total_elements=total_elements, 
                           shuffle_counts=session.get('shuffle_counts', {}))

@app.route("/get_level_data", methods=["POST"])
def get_level_data():
    selected_level = request.form.get("level")
    level_data = next((level for level in data if level["level"] == selected_level), None)
    
    if not level_data:
        return jsonify({"error": "Invalid level selected"})
    
    return jsonify({
        "data": level_data["data"],
        "shuffle_count": level_data.get("shuffle_count", 0)
    })

def get_max_shuffles(level_data):
    return level_data["data"][3]["value"]  # Now using index 3 for the shuffle limit

@app.route("/shuffle", methods=["POST"])
def shuffle():
    selected_level = request.form.get("level")
    level_data = next((level for level in data if level["level"] == selected_level), None)
    
    if not level_data:
        return jsonify({"error": "Invalid level selected"})
    
    max_shuffles = level_data.get("shuffle_count", 0)
    current_shuffles = session['shuffle_counts'][selected_level]
    
    if current_shuffles >= max_shuffles:
        return jsonify({"error": "No more shuffles available for this level"})
    
    # Filter out elements already in the body
    available_data = [item for item in level_data["data"] if item["element"] not in session['body']]
    
    if not available_data:
        return jsonify({"error": "All elements for this level have been collected"})
    
    # Extract the values and elements
    values = [float(item["value"]) for item in available_data]
    elements = [item["element"] for item in available_data]

    # Check if all weights are zero
    if sum(values) == 0:
        return jsonify({"error": "No elements available with non-zero weights"})

    # Ensure all values are numeric
    try:
        shuffled_element = random.choices(elements, weights=values, k=1)[0]
    except TypeError as e:
        print(f"Error: {e}")
        return jsonify({"error": "Non-numeric values found in weights"})

    # Add the won element to the body
    if shuffled_element not in session['body']:
        session['body'].append(shuffled_element)
        session.modified = True

    is_bonus = shuffled_element in bonus_elements
    
    # Check if all body elements are collected
    body_complete = all(element in session['body'] for element in body_elements)
    
    collected_count = len([el for el in session['body'] if el not in bonus_elements])
    
    # Increment the shuffle count for this level
    session['shuffle_counts'][selected_level] += 1
    
    return jsonify({
        "win": shuffled_element, 
        "is_bonus": is_bonus, 
        "body": session['body'],
        "body_complete": body_complete,
        "collected_count": collected_count,
        "total_elements": total_elements,
        "shuffles_left": max_shuffles - session['shuffle_counts'][selected_level],
        "max_shuffles": max_shuffles
    })

@app.route("/reset", methods=["POST"])
def reset():
    session['body'] = []
    session['shuffle_counts'] = {level_data["level"]: 0 for level_data in data}
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)