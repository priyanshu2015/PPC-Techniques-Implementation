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

app = Flask(__name__)
socketio = SocketIO(app)



"""
This is the computation server that will perform the homomorphic encryption operations.
It will receive the encrypted vectors from the bank server, perform the sum operation, and send back the result.

For it to work properly, the tenseal context must be the same as the one used in the bank server.

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


# storage for incoming requests
request_log = []

# Middleware that logs request data only for API routes
@app.before_request
def log_request_data():
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
        json_data = copy.deepcopy(request.get_json())  # Deep copy to avoid modifying original data

        # Truncate the data to limit the size being logged
        json_data['context'] = json_data['context'][:70] + "..."

        for i in range(len(json_data['encrypted_vectors'])):
            json_data['encrypted_vectors'][i] = json_data['encrypted_vectors'][i][:70] + "..."

        req_data['json_data'] = json_data
        req_data['data_size_bytes'] = request.content_length

    # Temporarily store request data for logging after the response
    request.req_data = req_data


# After request handler to log the response status code
@app.after_request
def log_response(response):
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

"""
# Middleware that logs request data only for API routes
@app.before_request
def log_request_data():
    r = request
    if not request.path.startswith('/api/'):
        return
    print("middleware triggered")
    r = request
    #print("middleware computing triggered")
    req_data = {
        "method": request.method,
        "path": request.path,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "remote_addr": request.remote_addr,
    }
    if request.method == 'POST':
        json_data = copy.deepcopy(request.get_json())  # deep copy to avoid modifying the original data

        # reduce the size of the data to be logged
        json_data['context'] = json_data['context'][:70] + "..."

        for i in range(len(json_data['encrypted_vectors'])):
            json_data['encrypted_vectors'][i] = json_data['encrypted_vectors'][i][:70] + "..."
        req_data['json_data'] = json_data
        req_data['data_size_bytes'] = request.content_length

    # Log the request to the request_log list
    request_log.append(req_data)
    socketio.emit('new_request', req_data)
"""


# API route to fetch the request log dynamically via polling
@app.route('/request_log')
def get_request_log():
    return jsonify(request_log)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/test')
def test():
    return jsonify("test")

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


if __name__ == '__main__':
    #app.run(debug=True, port=5500)
    socketio.run(app, debug=True, port=5500)
    #socketio.run(app, debug=True, port=5500)
