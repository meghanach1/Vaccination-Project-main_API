from datetime import date, datetime
from functools import wraps
import bcrypt
from bson import ObjectId, json_util
import certifi
from flask import Blueprint, json, jsonify, request, session
from bson import ObjectId
from flask_cors import cross_origin
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

vaccine_bp = Blueprint('vaccine', __name__)
# MongoDB connection string
mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client.VaccinationProject
patient_collection = db.Patients

@cross_origin(origin='http://localhost:3000')
@vaccine_bp.route('/get-vaccines', methods=['GET'])
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

        # Fetch data from MongoDB based on age
        vaccines = db.Vaccines.find({"ageGroup.min": {"$lte": age}, "ageGroup.max": {"$gte": age}})

        recommended = []
        required = []

        for vaccine in vaccines:
            if vaccine.get("required"):
                required.append({
                    "name": vaccine["name"],
                    "description": vaccine["description"],
                    "requiredDoses": vaccine["requiredDoses"],
                    "price": vaccine["price"]
                })

            if vaccine.get("recommended"):
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

@vaccine_bp.route('/api/get-locations', methods=['GET'])
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

@vaccine_bp.route('/api/get-time-slots', methods=['GET'])


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






@vaccine_bp.route('/<center_id>', methods=['GET'])

def get_location(center_id):
    try:
        # Retrieve patient details from Patients collection
        location = db.Vaccination_center.find_one({"_id": ObjectId(center_id)})
        
        # If patient not found, return 404
        if not location:
            return jsonify({'error': 'Patient not found'}), 404

        # Convert ObjectId to string for JSON serialization
        location['_id'] = str(location['_id'])

        # Prepare the output
        output = json.loads(json_util.dumps(location))

        return jsonify(output), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vaccine_bp.route('/manufacturer', methods=['GET'])
def get_manufacturer_data():
    selected_vaccine = request.args.get('selected_vaccine')

    if selected_vaccine is None:
        return jsonify({'error': 'Please provide a selected_vaccine parameter'}), 400

    # If selected_vaccine is a list, take the first element
    if isinstance(selected_vaccine, list):
        selected_vaccine = selected_vaccine[0]

    manufacturer_collection = db.Vaccination_category

    # Query the database for manufacturer data based on the selected vaccine
    result = manufacturer_collection.find_one({'name': selected_vaccine})

    if result is None:
        return jsonify({'error': f'Manufacturer data not found for the selected vaccine {selected_vaccine}'}), 404

    return jsonify({'vaccine': result['name'], 'manufacturer': result['manufacturer']})