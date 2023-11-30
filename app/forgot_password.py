from functools import wraps
import random
import string
import bcrypt
import certifi
from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from pymongo import MongoClient

forgotpassword_bp = Blueprint('forgotpassword', __name__)
@forgotpassword_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        email = request.json.get('email')
        password_reset_tokens = {}
        # Generate a random reset token
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        # Store the reset token (In a real app, store it in the database)
        password_reset_tokens[email] = reset_token

        # Send an email to the user with a link containing the reset token
        # (In a real app, use a library like Flask-Mail for sending emails)

        return jsonify({'message': 'Password reset initiated. Check your email for instructions.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
  