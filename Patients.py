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

from flask import Flask, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from functools import wraps

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
admin_collection = db.Admin
patient_collection = db.Patients
staff_collection = db.Vaccination_center_staff
bcrypt = Bcrypt(app)

# Define a decorator to check if the user is logged in
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Unauthorized'}), 401

            # Check if the user has the required role
            if role and session.get('role') != role:
                return jsonify({'error': 'Insufficient permissions'}), 403

            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
@app.route('/create_admin', methods=['POST'])
def create_admin():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Hash the password using Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create the admin document
        admin_document = {
            '_id': ObjectId(),
            'username': username,
            'password': hashed_password,
            'role': 'admin'
        }

        # Insert the admin document into the collection
        result = admin_collection.insert_one(admin_document)

        return jsonify({'message': 'Admin created successfully', 'admin_id': str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to handle admin login
@app.route('/login_admin', methods=['POST'])
def login_admin():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Find the admin in the database based on the provided username
        admin = admin_collection.find_one({'username': username})

        if admin and bcrypt.check_password_hash(admin['password'], password):
            # If the admin exists and the password is correct
            return jsonify({'message': 'Login successful for admin', 'admin_id': str(admin['_id']),'role': 'admin'}), 200
            print(f"passed")
        else:
            # If the admin does not exist or the password is incorrect
            return jsonify({'error': 'Invalid credentials'}), 401
            print(f"failed")

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_staff', methods=['POST'])
def create_staff():
    try:
        data = request.json

        # Extract staff data from the request
        username = data.get('username')
        password = data.get('password')
        staff_name = data.get('staff_name')
        appointments_managed = data.get('appointmentsManaged', 0)
        payments_handled = data.get('paymentsHandled', 0)

        # Hash the password using Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create the staff document
        staff_document = {
            '_id': ObjectId(),
            'username': username,
            'password': hashed_password,
            'role': 'staff',
            'staff_name': staff_name,
            'appointmentsManaged': appointments_managed,
            'paymentsHandled': payments_handled
        }

        # Insert the staff document into the collection
        result = staff_collection.insert_one(staff_document)

        return jsonify({
            'status': 'success',
            'message': 'Staff created successfully',
            'staff_id': str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/login_staff', methods=['POST'])
def login_staff():
    try:
        data = request.get_json()
        staff = staff_collection.find_one({'username': data['username']})

        if staff and bcrypt.check_password_hash(staff['password'], data['password']):
            session['user_id'] = str(staff['_id'])
            session['role'] = 'staff'
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'message': 'Invalid credentials'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_patient', methods=['POST'])
def create_patient():
    try:
        data = request.json

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        data['password'] = hashed_password

        # Insert data into MongoDB
        result = patient_collection.insert_one(data)
        return jsonify({"status": "success", "message": "Patient registered successfully", "inserted_id": str(result.inserted_id), "role": "Patient"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
@app.route('/login_patient', methods=['POST'])
def login_patient():
    try:
        data = request.json
        entered_password = data['password']

        # Find the patient by username
        patient = patient_collection.find_one({'username': data['username']})

        if patient and bcrypt.check_password_hash(patient['password'], entered_password):
            # Passwords match, return success
            print(f"valid credentials for {data['username']}")
            return jsonify({"status": "success", "message": "Patient login successful", "role": "Patient"})
        else:
            # Invalid username or password
            print(f"Invalid credentials for {data['username']}")
            return jsonify({"status": "error", "message": "Invalid username or password"})

    except Exception as e:
        print(f"Error during patient login: {str(e)}")
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
