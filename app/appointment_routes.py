import json
import ssl
import certifi
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from bson import ObjectId, json_util


mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client.VaccinationProject

# Your existing collections
appointments_collection = db.Appointments
patients_collection = db.Patients
vaccines_collection = db.Vaccines
vaccination_centers_collection = db.VaccinationCenters
appointment_bp = Blueprint('appointment', __name__)
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
        selected_location_name = data.get('selectedLocationName')

        # Mapping of location names to IDs
        location_name_mapping = {
        '655d0bf382d9f899c56eb14a': 'City Health Center',
      '655e96d41a133dcc3da819b2': 'Suburb Wellness Hub',
      '655e98a91a133dcc3dae00c7': 'Rural Health Clinic',
      '655e98cd1a133dcc3dae643d': 'University Medical Center',
      '655e9c7c1a133dcc3dbab297': 'Pediatric Vaccination Clinic',
      '655e9dae1a133dcc3dbe21c4': 'Elderly Care Vaccination Center',
        }

        # Get the corresponding ID for the selected location name
        selected_location_name = location_name_mapping.get(selected_location_name)

        if not selected_location_name:
            return jsonify({'error': 'Invalid location name'}), 400

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
            'selected_manufacturer': selected_manufacturer,
            'selected_location_name': selected_location_name,  # Add the selected location ID
        }
        result = appointments_collection.insert_one(appointment_doc)

        # Get the newly created appointment ID
        new_appointment_id = str(result.inserted_id)

        # Add the appointment ID to the response JSON
        response_data = {'message': 'Appointment added successfully', 'appointment_id': new_appointment_id}

        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/get_all_appointments', methods=['GET'])
def get_all_appointments():
    try:
        pipeline = [
        
          
            {
                '$project': {
                    '_id': {'$toString': '$_id'},
                    'selected_center_id': 1,
                    'Vaccination_center.center_name': 1,
                    'selected_vaccines_id': 1,
                    'patient_id': 1,
                    'full_name': 1,
                    'user_booking_date': 1,
                    'selected_timeslot': 1,
                    'selected_date': 1
                }
            }
        ]

        # Execute the aggregation pipeline
        result = appointments_collection.aggregate(pipeline)

        # Convert the result to a list and jsonify
        appointments = list(result)

        return jsonify({'appointments': appointments}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
    
def convert_to_json_serializable(appointment):
    appointment['_id'] = str(appointment['_id'])
    return appointment
@appointment_bp.route('/appointments/<patient_id>', methods=['GET'])
def get_appointments(patient_id):
    try:
        # Query MongoDB for appointments with the given patient_id
        appointments = appointments_collection.find({'patient_id': patient_id})

        # Convert MongoDB cursor to a list of dictionaries and make ObjectId serializable
        appointments_list = [convert_to_json_serializable(appointment) for appointment in appointments]

        # Return the appointments as JSON
        return jsonify({'appointments': appointments_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@appointment_bp.route('/update_appointment/<string:appointment_id>', methods=['PUT'])

def update_appointment(appointment_id):
    try:
        # Get the edited data from the request
        edited_data = request.json

        # Convert string to ObjectId for querying MongoDB
        appointment_id = ObjectId(appointment_id)

        # Exclude the '_id' field from the update
        edited_data.pop('_id', None)

        # Update the appointment in the database
        db.Appointments.update_one(
            {'_id': appointment_id},
            {'$set': edited_data}
        )

        return jsonify({'message': 'Appointment updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    try:
        # Get the edited data from the request
        edited_data = request.json

        # Convert string to ObjectId for querying MongoDB
        appointment_id = ObjectId(appointment_id)

        # Update the appointment in the database
        db.Appointments.update_one(
            {'_id': appointment_id},
            {'$set': edited_data}
        )

        return jsonify({'message': 'Appointment updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500