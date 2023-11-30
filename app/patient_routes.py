from functools import wraps
import bcrypt

import certifi
from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

patient_bp = Blueprint('patient', __name__)
# MongoDB connection string
mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client.VaccinationProject
patient_collection = db.Patients

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

@patient_bp.route('/create_patient', methods=['POST'])
def create_patient():
    try:
        print("Inside create patient")
        data = request.json

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        data['password'] = hashed_password.decode('utf-8')

        # Insert data into MongoDB
        result = patient_collection.insert_one(data)
        return jsonify({"status": "success", "message": "Patient registered successfully", "inserted_id": str(result.inserted_id), "role": "Patient"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@patient_bp.route('/login_patient', methods=['POST'])
def login_patient():
    print("Inside login_patient")
    try:
        data = request.json
        entered_password = data['password'].encode('utf-8')

        # Find the patient by username
        patient = patient_collection.find_one({'username': data['username']})

        if patient and bcrypt.checkpw(entered_password, patient['password'].encode('utf-8')):
            # Passwords match, return success
            print(f"valid credentials for {data['username']}")
            return jsonify({"status": "success", "message": "Patient login successful", "role": "Patient","patient_id": str(patient['_id'])})
        else:
            # Invalid username or password
            print(f"Invalid credentials for {data['username']}")
            return jsonify({"status": "error", "message": "Invalid username or password"})

    except Exception as e:
        print(f"Error during patient login: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

password_reset_tokens = {}

@patient_bp.route('/save-medical-history', methods=['POST'])
def save_medical_history():
    try:
        data = request.get_json()

        # Access the Patient_History collection
        patient_history_collection = db.Patient_History

        # Save data to MongoDB
        patient_history_collection.insert_one(data)

        return jsonify(message='Medical history data saved successfully'), 201
    except Exception as e:
        print(f'Error saving medical history data: {e}')
        return jsonify(message='Internal server error'), 500
