import certifi
from flask import Blueprint, Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

appointment_bp = Blueprint('appointment', __name__)
mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client.VaccinationProject
appointments_collection=db.Appointments
@appointment_bp.route('/insert_appointment', methods=['POST'])
def insert_appointment():
    try:
        # Get data from the request
        data = request.json
        selected_center_id = data.get('selected_center_id')
        selected_vaccines_id = data.get('selected_vaccines_id', []) 
        patient_id = data.get('patient_id')
        user_booking_date = data.get('user_booking_date', datetime.now())
        booking_type = data.get('booking_type')
        status = data.get('status', 'pending')
        selected_timeslot = data.get('selected_timeslot')
        selected_date = data.get('selected_date')
        selected_manufacturer = data.get('selected_manufacturer', None)

        # Determine booking type based on user role
        if 'user_role' in data and data['user_role'] == 'patient':
            booking_type = 'online'
        else:
            booking_type = 'walkin'

        # Create appointment document
        appointment_doc = {
        
            'selected_center_id': selected_center_id,
            'selected_vaccines_id': selected_vaccines_id,
            'patient_id': patient_id,
            'user_booking_date': user_booking_date,
            'booking_type': booking_type,
            'status': status,
            'selected_timeslot': selected_timeslot,
            'selected_date': selected_date,
            'selected_manufacturer': selected_manufacturer
        }

        # Insert document into the MongoDB collection
        appointments_collection.insert_one(appointment_doc)

        return jsonify({'message': 'Appointment added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
