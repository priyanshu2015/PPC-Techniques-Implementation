from flask import Flask, request, jsonify
from schnorr_core import ZK, ZKSignature, ZKData
import requests
import json
import base64

app = Flask(__name__)

# Dummy user database (replace with a real database)
proof = None

def encode_bytes(obj):
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    if isinstance(obj, dict):
        return {k: encode_bytes(v) for k, v in obj.items()}
    return obj

def decode_bytes(obj):
    if isinstance(obj, str):
        # Try to decode Base64 strings, otherwise return as is
        try:
            return base64.b64decode(obj.encode('utf-8'))
        except Exception:
            return obj
    elif isinstance(obj, dict):
        # Decode Base64 strings in dictionaries
        return {k: decode_bytes(v) for k, v in obj.items()}
    return obj


@app.route('/login', methods=['POST'])
def login():
    global proof
    client_zk = ZK.new(curve_name="secp256k1", hash_alg="sha3_256")

    password = "password123"

    # Create signature and send to server
    signature = client_zk.create_signature(password).to_json()

    # Receive the token from the server
    token = requests.post("http://127.0.0.1:6000/login", json={"signature": signature}, headers={
        "Content-Type": "application/json"
    }).json()["token"]

    # Create a proof that signs the provided token and sends to server
    proof = client_zk.sign(password, token)

    return jsonify({"message": "Login successful"})


@app.route('/private_route', methods=['POST'])
def private_route():
    global proof

    # Verify the proof
    if not proof:
        return jsonify({"error": "No proof provided"}), 400

    proof_to_send = proof.to_json()

    response = requests.post("http://127.0.0.1:6000/compute", json={
        "proof": proof_to_send
    }).json()

    return jsonify({"payload": response})


if __name__ == '__main__':
    app.run(debug=True)