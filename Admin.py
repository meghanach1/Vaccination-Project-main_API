from flask import Flask, request
import pymongo , json

#Creating the Flask app
app=Flask(__name__)

#Connecting to the Database
client = pymongo.MongoClient("mongodb+srv://Project:bmnp12105@cluster0.vgwcjai.mongodb.net/")
db = client.VaccinationProject

#Post Request to insert a new record
@app.route('/admin', methods=['POST'])
def admin_record():
    json = request.json
    id = db.Admin.insert_one(json)
    return "Admin Record was created sucessfully"

if __name__ == '__main__':
    app.run()
