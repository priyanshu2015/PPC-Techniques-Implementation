from flask import Blueprint, render_template, request, jsonify

import requests
import secrets


smpc_bp = Blueprint('smpc', __name__)

@smpc_bp.route('/test')
def login():
    return "This is the smpc page."


@smpc_bp.route('/generate_secret', methods=['GET', 'POST'])
def generate_secret_key():
    # generate a secret key
    secret_key = secrets.token_bytes(16)
    integer_secret_key = int.from_bytes(secret_key, byteorder='big')
    print(integer_secret_key)
    return str(integer_secret_key)
