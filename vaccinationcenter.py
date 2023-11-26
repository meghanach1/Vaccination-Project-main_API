# Add this route to your Flask app
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("your_mongo_uri")
db = client['your_db_name']
vaccination_centers = db['VaccinationCenters']

@app.route('/api/get-locations', methods=['GET'])
def get_locations():
    try:
        selected_date_str = request.args.get('selectedDate')

        # Check if selected_date_str is provided, otherwise, return an error response
        if not selected_date_str:
            return jsonify({'error': 'Selected date is missing'}), 400

        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        # Query the collection based on the selected date
        result = vaccination_centers.find({
            'dateAvailability.date': selected_date
        })

        locations = []

        # Extract locations from the result
        for center in result:
            locations.extend(center['locations'])

        return jsonify(locations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
