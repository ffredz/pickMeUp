from flask import Flask, jsonify, request, render_template
import json
import os

app = Flask(__name__)

data_storage = []
bag_counter = 1  # Start from bag number 1
latest_measurement = {"weight": 0}
stored_measurements = []
session_data = []  # To store saved sessions
counter = 1

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/storage')
def storage():
    return render_template('storage.html')
# Endpoint to register a measurement (updates the latest measurement)
@app.route('/register-measurement', methods=['POST'])
def register_measurement():
    global latest_measurement
    if request.is_json:
        data = request.get_json()
        latest_measurement["weight"] = data.get("weight", 0)
        return jsonify({"status": "success", "latest_measurement": latest_measurement}), 200
    return jsonify({"status": "error", "message": "Invalid JSON"}), 400

# Endpoint to store the latest registered measurement
@app.route('/store-measurement', methods=['POST'])
def store_measurement():
    global counter, latest_measurement, stored_measurements
    if latest_measurement["weight"] is not None:
        stored_measurements.append({
            "bag_nr": f"Bag nr {counter}",
            "weight": latest_measurement["weight"]
        })
        counter += 1
        return jsonify({"status": "success", "stored_measurements": stored_measurements}), 200
    return jsonify({"status": "error", "message": "No measurement to store"}), 400


# Endpoint to clear all stored measurements
@app.route('/clear-data', methods=['POST'])
def clear_data():
    global stored_measurements, bag_counter
    stored_measurements = []
    bag_counter = 1
    return jsonify({"status": "success", "message": "All data cleared"}), 200

# Endpoint to get all stored measurements and the latest measurement
@app.route('/get-data', methods=['GET'])
def get_data():
    return jsonify({
        "latest_measurement": latest_measurement,
        "stored_measurements": stored_measurements
    }), 200

# Endpoint to save the current session and reset the data
@app.route('/save-session', methods=['POST'])
def save_session():
    global stored_measurements, bag_counter, session_data
    
    # Calculate session totals
    total_weight = sum(item["weight"] for item in stored_measurements)
    total_bags = len(stored_measurements)

    # Save session data with totals
    session = {
        "session_id": len(session_data) + 1,
        "measurements": stored_measurements,
        "total_bags": total_bags,
        "total_weight": total_weight
    }
    session_data.append(session)

    # Save to JSON file (for persistence across restarts)
    with open('sessions.json', 'w') as f:
        json.dump(session_data, f, indent=4)

    # Reset stored measurements and bag counter
    stored_measurements = []
    bag_counter = 1

    return jsonify({"status": "success", "message": "Session saved successfully"}), 200

# Endpoint to retrieve all sessions
@app.route('/get-sessions', methods=['GET'])
def get_sessions():
    return jsonify(session_data), 200
@app.route('/remove-latest', methods=['POST'])
def remove_latest():
    global counter
    if stored_measurements:
        stored_measurements.pop()  # Remove the last element from the list
        counter = max(1, len(stored_measurements) + 1)  # Adjust the counter
    return jsonify({"status": "success", "message": "Latest measurement removed"}), 200

# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
