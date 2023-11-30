from functools import wraps
import bcrypt
import certifi
from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from pymongo import MongoClient
from flask_cors import cross_origin

admin_bp = Blueprint('admin', __name__)
# MongoDB connection string
mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())

# Connect to the database
db = client.VaccinationProject
admin_collection = db.Admin

@admin_bp.route('/create_admin', methods=['POST'])
def create_admin():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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

# Route to handle admin login
@admin_bp.route('/login_admin', methods=['POST'])
def login_admin():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password').encode('utf-8')

        # Find the admin in the database based on the provided username
        admin = admin_collection.find_one({'username': username})

        if admin and bcrypt.checkpw(password, admin['password'].encode('utf-8')):
            # If the admin exists and the password is correct
            return jsonify({'message': 'Login successful for admin', 'admin_id': str(admin['_id']),'role': 'admin'}), 200
            print(f"passed")
        else:
            # If the admin does not exist or the password is incorrect
            return jsonify({'error': 'Invalid credentials'}), 401
            print(f"failed")

    except Exception as e:
        return jsonify({'error': str(e)}), 500
