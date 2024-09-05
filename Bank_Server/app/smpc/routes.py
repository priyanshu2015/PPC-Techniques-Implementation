from flask import Blueprint, render_template, request, jsonify

import requests
import secrets


smpc_bp = Blueprint('smpc', __name__)

@smpc_bp.route('/test')
def login():
    return "This is the smpc page."


secret_key = None
secret_key_shares = []

#@smpc_bp.route('/generate_secret', methods=['GET', 'POST'])
@smpc_bp.route('/generate_secret', methods=['GET'])
def generate_secret_key():
    number_of_shares = request.args.get('shares')
    threshold = request.args.get('threshold')
    global secret_key
    # generate a secret key
    secret_bytes = secrets.token_bytes(16)
    secret_key = int.from_bytes(secret_bytes, byteorder='big')
    print(secret_key)
    return str(secret_key)

