import json
import random
import string
import certifi
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId, json_util
from flask_cors import cross_origin
from datetime import date, datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


# MongoDB connection string
mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())

# Connect to the database
db = client.VaccinationProject

# Define the collection
collection = db.Patients

@app.route('/insert_data', methods=['POST'])
def insert_data():
    try:
        data = request.json
        # Insert data into MongoDB
        result = collection.insert_one(data)
        return jsonify({"status": "success", "message": "Data inserted successfully", "inserted_id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
password_reset_tokens = {}

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        email = request.json.get('email')

        # Generate a random reset token
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        # Store the reset token (In a real app, store it in the database)
        password_reset_tokens[email] = reset_token

        # Send an email to the user with a link containing the reset token
        # (In a real app, use a library like Flask-Mail for sending emails)

        return jsonify({'message': 'Password reset initiated. Check your email for instructions.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/vaccines', methods=['GET'])
@cross_origin(origin='http://localhost:3001')
def get_vaccines():
    try:
        age = request.args.get('age')

        # Check if age is provided, otherwise, return an error response
        if not age:
            return jsonify({'error': 'Age is missing'}), 400

        # If age is a list, take the first element
        age = age[0] if isinstance(age, list) else age

        # Convert age to an integer
        age = int(age)

        vaccines = db.Vaccines.find({"ageGroup.min": {"$lte": age}, "ageGroup.max": {"$gte": age}})
        recommended = []
        required = []
        for vaccine in vaccines:
            if vaccine["required"]:
                required.append({
                    "name": vaccine["name"],
                    "description": vaccine["description"],
                    "requiredDoses": vaccine["requiredDoses"],
                    "price": vaccine["price"]
                })
            if vaccine["recommended"]:
                recommended.append({
                    "name": vaccine["name"],
                    "description": vaccine["description"],
                    "requiredDoses": vaccine["requiredDoses"],
                    "price": vaccine["price"]
                })  
        output = json.loads(json_util.dumps({"recommended": recommended, "required": required}))
        return jsonify(output)
    except Exception as e:
        print(f"Error in /vaccines route: {e}")
        return jsonify({"error": str(e)}), 500


def convert_dates_to_strings(obj):
    if isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, list):
        return [convert_dates_to_strings(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_dates_to_strings(value) for key, value in obj.items()}
    else:
        return obj
@app.route('/api/get-locations', methods=['GET'])


def get_locations():
    try:
        selected_date_str = request.args.get('selectedDate')
        
        print('Received selected date:', selected_date_str)
        # If selected_date_str is a list, take the first element
        selected_date_str = selected_date_str[0] if isinstance(selected_date_str, list) else selected_date_str

        selected_date = datetime.fromisoformat(selected_date_str).date()
        vaccination_centers = db['Vaccination_center']

        # Query the collection based on the selected date
        result = vaccination_centers.find({
            'availableDates': {'$elemMatch': {'$eq': selected_date_str}}
        }, {'center_name': 1, 'location': 1, '_id': 1})

        # Convert datetime.date objects to strings using the helper function
        locations = [
    {
        'center_name': doc['center_name'],
        'location': doc['location'],
        '_id': str(doc['_id'])
    }
    for doc in result
]
        return jsonify(locations)

    except ValueError as ve:
        return jsonify({'error': f'Error parsing date: {str(ve)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-time-slots', methods=['GET'])


def get_time_slots():
    try:
        # Get the selected ID from the request parameters
        selected_ids = request.args.getlist('selectedId')
        print('Received selected date:', selected_ids)
        # Convert each selected ID to ObjectId
        selected_ids = [ObjectId(id) for id in selected_ids]

        # Query the collection based on the selected IDs
        vaccination_centers = db['Vaccination_center']
        result = vaccination_centers.find({'_id': {'$in': selected_ids}})

        if result:
            # Extract available time slots from the result
            available_time_slots = []
            for center in result:
                center_id = str(center['_id'])
                time_slots = center.get('availableTimeSlots', [])
                available_time_slots.append({'centerId': center_id, 'timeSlots': time_slots})

            return jsonify({'availableTimeSlots': available_time_slots})
        else:
            return jsonify({'error': 'Vaccination centers not found'})

    except Exception as e:
        return jsonify({'error': str(e)})
if __name__ == '__main__':
    app.run(debug=True)
