import certifi
from flask import Blueprint, Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

payment_bp = Blueprint('payment', __name__)
mongo_uri = "mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client.VaccinationProject
payments_collection=db.Payments


@app.route('/api/payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()

        # Extract data from the request
        patient_id = data.get('patient_id')
        appointment_id = data.get('appointment_id')
        date_paid = data.get('date_paid')
        amount = data.get('amount')
        payment_method = data.get('payment_method')

        # Validate the required fields
        if not all([patient_id, appointment_id, date_paid, amount, payment_method]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Create a payment document
        payment_data = {
            'patient_id': ObjectId(patient_id),
            'appointment_id': ObjectId(appointment_id),
            'date_paid': date_paid,
            'amount': amount,
            'payment_method': payment_method
        }

        # Insert the payment document into the MongoDB collection
        result = mongo.db.payments.insert_one(payment_data)

        # Return the ID of the newly created payment document
        return jsonify({'payment_id': str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)