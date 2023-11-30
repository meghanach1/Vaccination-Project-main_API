# main.py
import os
from flask import Flask
from flask_cors import CORS
from admin_routes import admin_bp
from patient_routes import patient_bp
from staff_routes import staff_bp
from forgot_password import forgotpassword_bp
from vaccine_routes import vaccine_bp
from appointment_routes import appointment_bp
from flask_bcrypt import Bcrypt

# Generate a secret key
def generate_secret_key():
    return os.urandom(24).hex()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'  # Set a unique and secret key
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
    bcrypt = Bcrypt(app)
  
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(forgotpassword_bp, url_prefix='/forgotpassword')
    app.register_blueprint(vaccine_bp, url_prefix='/vaccine')
    app.register_blueprint(appointment_bp, url_prefix='/appointment')
    

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
