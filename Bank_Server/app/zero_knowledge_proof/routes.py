from flask import Blueprint, jsonify, request
import requests
import sys
import os

# Adjust the system path to include the parent directory of the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from zero_knowledge_proof.schnorr_core import ZK

# Create a Blueprint for Zero-Knowledge Proof (ZKP) related routes
zkp_bp = Blueprint('zkp', __name__)

# Global variable to store proof
proof = None

"""
This file contains the routes for the Zero-Knowledge Proof (ZKP) backend.
"""

@zkp_bp.route('/login', methods=['GET'])
def login():
    """
    Handle the login route. This route performs the following:
    - Creates a ZKP signature for the password.
    - Sends the signature to the server to obtain a token.
    - Signs the token to generate a proof.

    Returns:
        JSON response with a success message and the generated proof.
    """
    global proof
    # Initialize a new ZKP instance with secp256k1 curve and sha3_256 hash algorithm
    client_zk = ZK.new(curve_name="secp256k1", hash_alg="sha3_256")

    # Sample password for demonstration
    password = "password123"

    # Create a signature for the password
    signature = client_zk.create_signature(password).to_json()

    # Send the signature to the server and receive a token
    token = requests.post("http://127.0.0.1:5500/api/login", json={"signature": signature}, headers={
        "Content-Type": "application/json"
    }).json()["token"]

    # Create a proof by signing the token
    proof = client_zk.sign(password, token)

    # Return the proof as a JSON response
    return jsonify({"message": "Login successful", "proof": proof.to_json()})


@zkp_bp.route('/private_route', methods=['GET'])
def private_route():
    """
    Demonstrates the use of the proof to access a private route.
    - Verifies the proof by sending it to the server.

    Returns:
        JSON response with the payload received from the server if proof verification is successful.
    """
    global proof

    # Check if proof exists
    if not proof:
        return jsonify({"error": "No proof provided. Log in first"}), 400

    # Convert proof to JSON format
    proof_to_send = proof.to_json()

    # Send the proof to the server for verification
    response = requests.post("http://127.0.0.1:5500/api/private_route", json={
        "proof": proof_to_send
    }).json()

    # Return the response payload
    return jsonify({"payload": response})
