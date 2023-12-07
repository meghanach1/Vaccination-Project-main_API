from json import dumps
import json
from urllib import response
import certifi
from flask import Blueprint, Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId 
from bson import ObjectId, json_util
from flask_cors import cross_origin

payment_bp = Blueprint('payment', __name__)
mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client.VaccinationProject
payments_collection=db.Payments



@payment_bp.route('/create_payment', methods=['POST'])
@cross_origin(origin='http://localhost:3000')
def create_payment():
    try:
        data = request.get_json()

        # Extract data from the request
        payment_id = data.get('payment_id')
        patient_id = data.get('patient_id')
        date_paid = data.get('date_paid')
        appointment_id =data.get('appointment_id')
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        payment_status = data.get('payment_status')

        # Validate the required fields
        if not all([patient_id,appointment_id, amount,payment_status]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Create a payment document
        payment_data = {
            'payment_id':  ObjectId(payment_id),
            'patient_id': patient_id,
            'appointment_id': ObjectId(appointment_id),
            'date_paid': date_paid,
            'amount': amount,
            'payment_method': payment_method,
            'payment_status':payment_status
        }

        # Insert the payment document into the MongoDB collection
        result = db.Payments.insert_one(payment_data)

        # Return the ID of the newly created payment document
        return jsonify({'payment_id': str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def convert_to_json_serializable(patient):
    patient['_id'] = str(patient['_id'])
    return patient


@payment_bp.route('/get_payment_details', methods=['GET'])
def get_payment_details():
    try:
        pipeline = [
            {
                '$project': {
                    'appointment_id': {'$toString': '$appointment_id'},
                    'Patients.full_name': 1,
                    'Patients.email': 1,
                    'Patients.age': 1,
                    'patient_id': {'$toString': '$patient_id'},
                    'amount': 1,
                    'payment_status': 1
                }
            }
        ]

        # Execute the aggregation pipeline
        result = payments_collection.aggregate(pipeline)

        # Convert the result to a list and manually convert ObjectId to string
        payments = [
            {**doc, '_id': str(doc['_id'])} for doc in result
        ]

        return jsonify({'payments': payments}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    


@payment_bp.route('/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    try:
        # Retrieve patient details from Patients collection
        payment = db.Payments.find_one({"_id": ObjectId(patient_id)})
        
        # If patient not found, return 404
        if not payment:
            return jsonify({'error': 'Patient not found'}), 404

        # Merge firstName and lastName into full_name
       
        # Convert ObjectId to string for JSON serialization
        payment['_id'] = str(payment['_id'])

        # Prepare the output
        output = json.loads(json_util.dumps(payment))

        return jsonify(output), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@payment_bp.route('/payment/update_payment/<payment_id>', methods=['OPTIONS'])
def handle_options_request(payment_id):
    return '', 200, {'Access-Control-Allow-Origin': 'http://localhost:3000', 'Access-Control-Allow-Methods': 'PUT', 'Access-Control-Allow-Headers': 'Content-Type'}


@payment_bp.route('/update_payment_status/<payment_id>', methods=['PUT'])
@cross_origin(origin='http://localhost:3000')
def update_payment(payment_id):
    try:
        # Ensure the provided patient_id is a valid ObjectId
        if not ObjectId.is_valid(payment_id):
            return jsonify({"error": "Invalid payment ID"}), 400
        
        # Find the patient by ID
        payment = db.Payments.find_one({"_id": ObjectId(payment_id)})

        if not payment:
            return jsonify({"error": "payment not found"}), 404

        # Get the updated data from the request JSON
        updated_data = request.get_json()

        # Update the patient's fields
        db.Payments.update_one({"_id": ObjectId(payment_id)}, {"$set": updated_data})

        return jsonify({"message": "Patient updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
