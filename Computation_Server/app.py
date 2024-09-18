import json
from threading import Thread
from time import perf_counter

from flask import Flask, request, jsonify, render_template
import datetime
from flask_socketio import SocketIO

import pandas as pd
import tenseal as ts
import io
import traceback
import base64

import copy

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zero_knowledge_proof.schnorr_core import ZK, ZKSignature, ZKData

app = Flask(__name__)
socketio = SocketIO(app)

"""
This is the computation server that will perform the homomorphic encryption operations.
It will receive the encrypted vectors from the bank server, perform the sum operation, and send back the result.

For it to work properly, the tenseal context must be the same as the one used in the bank server. Therefore, the
context is sent along with the encrypted vectors.
"""


def serialize_encrypted_vector(encrypted_vectors: ts.bfv_vector) -> str:
    """
    Serialize the encrypted vector to bytes and then to base64
    :param encrypted_vectors: encrypted vector
    :return: serialized encrypted vector
    """
    bytes = encrypted_vectors.serialize()
    serialized = base64.b64encode(bytes).decode('utf-8')
    return serialized


def serialize_encrypted_vectors(encrypted_vectors: list[ts.bfv_vector]) -> list[str]:
    """
    Serialize the encrypted vectors to bytes and then to base64
    :param encrypted_vectors: list of encrypted vectors
    :return: list of serialized encrypted vectors
    """

    serialized_vectors = []
    for v in encrypted_vectors:
        serialized = serialize_encrypted_vector(v)
        serialized_vectors.append(serialized)
    return serialized_vectors


def deserialize_encrypted_vectors(context, serialized_vectors: list[bytes]) -> list[ts.bfv_vector]:
    """
    Deserialize the encrypted vectors from base 64 to bytes to ts.bfv_vector
    :param serialized_vectors: list of serialized encrypted vectors
    :return: list of encrypted vectors
    """
    encrypted_vectors = []
    for s in serialized_vectors:
        bytes = base64.b64decode(s)
        encrypted_vectors.append(ts.bfv_vector_from(context, bytes))
    return encrypted_vectors


def truncate_dict(d: dict, max_length: int) -> dict:
    """
    Truncate the dictionary values to the specified length
    :param d: dictionary
    :param max_length: maximum length of the values
    :return: dictionary with truncated values
    """
    for key in d:
        if isinstance(d[key], str):
            d[key] = d[key][:max_length] + "..."

        # Recursively truncate nested dictionaries
        if isinstance(d[key], dict):
            d[key] = truncate_dict(d[key], max_length)

        # Recursively truncate nested lists
        if isinstance(d[key], list):
            for i in range(len(d[key])):
                if isinstance(d[key][i], str):
                    d[key][i] = d[key][i][:max_length] + "..."
    return d


# storage for incoming requests
request_log = []



@app.before_request
def log_request_data():
    """
    Middleware that logs request data only for API routes
    :return:
    """
    if not request.path.startswith('/api/'):
        return
    req_data = {
        "method": request.method,
        "path": request.path,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "remote_addr": request.remote_addr,
    }

    # If the request is a POST, log its JSON data
    if request.method == 'POST':
        req_data['data_size_bytes'] = request.content_length

        json_data = copy.deepcopy(request.get_json())  # Deep copy to avoid modifying original data
        req_data['json_data'] = truncate_dict(json_data, 70)

    # Temporarily store request data for logging after the response
    request.req_data = req_data


@app.after_request
def log_response(response):
    """
    After request handler to log the response status code
    :param response:
    :return:
    """
    # Only log for API routes
    if not request.path.startswith('/api/'):
        return response

    # Add the response status code to the log data
    request.req_data['status_code'] = response.status_code

    # Log the full request and response data
    request_log.append(request.req_data)

    # Emit the logged request data via socketio (if needed)
    socketio.emit('new_request', request.req_data)

    return response


@app.route('/request_log')
def get_request_log():
    """
    This route is used to fetch the request log data initially and the new data via the websocket
    :return:
    """
    return jsonify(request_log)


@app.route('/')
def home():
    """
    Render the GUI
    :return:
    """
    return render_template('index.html')


@app.route('/api/compute-sum', methods=['POST'])
def compute_sum():
    """
    This route is used to compute the sum of encrypted vectors.

    The JSON data should contain the following fields:
    - encrypted_vectors: list of base64-encoded encrypted vectors
    - context: base64-encoded tenseal context
    - number_of_elements: number of elements in the encrypted vectors
    :return:
    """
    start = perf_counter()

    print("Received request to compute sum of encrypted vectors")
    json_data = request.json

    encrypted_base64_vectors = json_data["encrypted_vectors"]
    context_encoded = json_data['context']
    number_of_elements = json_data["number_of_elements"]

    context_serialized = base64.b64decode(context_encoded)
    context = ts.context_from(context_serialized)

    encrypted_vectors = deserialize_encrypted_vectors(context, encrypted_base64_vectors)

    encrypted_sum = encrypted_vectors[0].sum()
    for s in encrypted_vectors[1:]:
        encrypted_sum += s.sum()

    serialized_data = serialize_encrypted_vector(encrypted_sum)

    print("Computed sum of encrypted vectors, sending back to Bank Server")
    end = perf_counter()
    print(f"Time taken: {end - start} seconds")
    return jsonify({"sum": serialized_data})


@app.route('/api/compute-sum-single', methods=['POST'])
def compute_sum_single():
    """
    this is for testing purposes only
    :return:
    """
    # Parse the JSON data
    json_data = request.json
    json_data = json.loads(json_data)

    context_encoded = json_data['context']
    bsv_encoded = json_data['bsv_vector']

    context_serialized = base64.b64decode(context_encoded)
    context = ts.context_from(context_serialized)

    # Decode the base64 string back to bytes
    bsv_serialized = base64.b64decode(bsv_encoded)

    # Deserialize the encrypted BSV vector
    encrypted_bsv = ts.bfv_vector_from(context, bsv_serialized)

    # Perform the sum operation on the vector
    result_encrypted = encrypted_bsv.sum()

    # Serialize and base64-encode the result to send back in JSON format
    result_serialized = result_encrypted.serialize()
    result_encoded = base64.b64encode(result_serialized).decode('utf-8')

    # Return the result in JSON
    return jsonify({'sum': result_encoded}), 200


server_password = "SecretServerPassword"
jwt_secret = "JWTSecretKey"
server_zk = ZK.new(curve_name="secp384r1", hash_alg="sha3_512", jwt_secret=jwt_secret)
server_signature: ZKSignature = server_zk.create_signature("SecureServerPassword")
client_signature = None



@app.route('/api/login', methods=['POST'])
def login():
    """
    This route is used to authenticate the client using ZKP and generate a token for the client.
    :return:
    """
    global server_password

    signature = request.json.get("signature")

    client_signature = ZKSignature.from_json(signature)

    # client_zk = ZK(client_signature.params)

    # print(client_zk.token())

    jwt = server_zk.jwt(client_signature)

    token = server_zk.sign("SecureServerPassword", jwt)

    token = token.to_json()

    return jsonify({"token": token})


@app.route('/api/private_route', methods=['POST'])
def compute():
    """
    This route is a private route that requires the client to authenticate using ZKP.
    """
    global server_signature
    global client_signature
    global server_zk

    if client_signature is None:
        return jsonify({"error": "Not authenticated"}), 401


    proof = request.json.get("proof")
    proof = ZKData.from_json(proof)
    token = ZKData.from_json(proof.data)

    data = server_zk.verify_jwt(token.data)
    client_signature = ZKSignature.from_json(data["signature"])
    client_zk = ZK(client_signature.params)

    if not server_zk.verify(token, server_signature):
        return jsonify({"error": "Invalid proof"}), 403
    else:
        if not client_zk.verify(proof, client_signature, data=token):
            return jsonify({"error": "Invalid proof"}), 403

    return jsonify({"message": "Access Granted"})


if __name__ == '__main__':
    # app.run(debug=True, port=5500)
    socketio.run(app, debug=True, port=5500)
    # socketio.run(app, debug=True, port=5500)
