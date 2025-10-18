from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()


SUP_URL = os.getenv("SUP_URL")
SUP_KEY = os.getenv("SUP_KEY")

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            return jsonify({
                "message": "User registered successfully!",
                "user": response.user.email
            }), 201
        else:
            return jsonify({"error": "Registration failed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.session:
            return jsonify({
                "message": "Login successful!",
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": response.user.email
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400
