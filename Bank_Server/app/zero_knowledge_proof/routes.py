from flask import Blueprint, render_template, jsonify, request, app
import requests

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from zero_knowledge_proof.schnorr_core import ZK

zkp_bp = Blueprint('zkp', __name__)

proof = None

"""
This file contains the routes for the Zero-Knowledge-Proof backend routes.
"""


@zkp_bp.route('/login', methods=['GET'])
def login():
    global proof
    client_zk = ZK.new(curve_name="secp256k1", hash_alg="sha3_256")

    password = "password123"

    # Create signature and send to server
    signature = client_zk.create_signature(password).to_json()

    # Receive the token from the server
    token = requests.post("http://127.0.0.1:5500/api/login", json={"signature": signature}, headers={
        "Content-Type": "application/json"
    }).json()["token"]

    # Create a proof that signs the provided token and sends to server
    proof = client_zk.sign(password, token)
    # return proof.to_json()
    return jsonify({"message": "Login successful", "proof": proof.to_json()})


@zkp_bp.route('/private_route', methods=['GET'])
def private_route():
    """
    This route is a helper route to demonstrate the use of the proof.
    It takes the saved proof and sends it to the server to verify and access the private route.
    :return:
    """
    global proof

    # Verify the proof
    if not proof:
        return jsonify({"error": "No proof provided. Loging first"}), 400

    proof_to_send = proof.to_json()

    response = requests.post("http://127.0.0.1:5500/api/private_route", json={
        "proof": proof_to_send
    }).json()

    return jsonify({"payload": response})