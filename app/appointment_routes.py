import ssl
import certifi
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime


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

    try:
        pipeline = [
            {
                '$lookup': {
                    'from': 'Vaccination_center',
                    'localField': 'selected_center_id',
                    'foreignField': '_id',
                    'as': 'Vaccination_center'
                }
            },
            {
                '$lookup': {
                    'from': 'Vaccines',
                    'localField': 'selected_vaccines_id',
                    'foreignField': '_id',
                    'as': 'Vaccines'
                }
            },
            {
                '$lookup': {
                    'from': 'Patients',
                    'localField': 'patient_id',
                    'foreignField': '_id',
                    'as': 'Patients'
                }
            },
            {
                '$addFields': {
                    'full_name': {
                        '$concat': [
                            {'$ifNull': [{'$arrayElemAt': ['$Patients.firstName', 0]}, '']},
                            ' ',
                            {'$ifNull': [{'$arrayElemAt': ['$Patients.lastName', 0]}, '']}
                        ]
                    }
                }
            },
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

    try:
        pipeline = [
            {
                '$lookup': {
                    'from': 'Vaccination_center',
                    'localField': 'selected_center_id',
                    'foreignField': '_id',
                    'as': 'Vaccination_center'
                }
            },
            {
                '$lookup': {
                    'from': 'Vaccines',
                    'localField': 'selected_vaccines_id',
                    'foreignField': '_id',
                    'as': 'Vaccines'
                }
            },
            {
                '$lookup': {
                    'from': 'Patients',
                    'localField': 'patient_id',
                    'foreignField': '_id',
                    'as': 'Patients'
                }
            },
           
            {
                '$project': {
                    '_id': {'$toString': '$_id'},
                    'selected_center_id': 1,
                    'Vaccination_center.center_name': 1,
                    'selected_vaccines_id': 1,
                    'patient_id': 1,
                    'Patients.first_name': 1,
                    'user_booking_date': 1,
                    'selected_timeslot': 1,
                    'selected_date': 1
                }
            }
        ]
       
        # Execute the aggregation pipeline
       

        result_cursor = appointments_collection.aggregate(pipeline)
        appointments = list(result_cursor)
        print(appointments)

        return jsonify({'appointments': appointments}), 200

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