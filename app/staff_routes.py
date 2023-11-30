import bcrypt
import certifi
from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

staff_bp = Blueprint('staff', __name__)

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


@staff_bp.route('/create_staff', methods=['POST'])
def create_staff():
    try:
        data = request.json

        # Extract staff data from the request
        username = data.get('username')
        password = data.get('password')
        staff_name = data.get('staff_name')
        appointments_managed = data.get('appointmentsManaged', 0)
        payments_handled = data.get('paymentsHandled', 0)

        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Create the staff document
        staff_document = {
            '_id': ObjectId(),
            'username': username,
            'password': hashed_password.decode('utf-8'),
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

@staff_bp.route('/login_staff', methods=['POST'])
def login_staff():
    try:
        data = request.get_json()
        staff = staff_collection.find_one({'username': data['username']})

        if staff and bcrypt.checkpw(data['password'].encode('utf-8'), staff['password'].encode('utf-8')):
            session['user_id'] = str(staff['_id'])
            session['role'] = 'staff'
            return jsonify({'message': 'Login successful',"staff_id": str(staff['_id'])})
        else:
            return jsonify({'message': 'Invalid credentials'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
