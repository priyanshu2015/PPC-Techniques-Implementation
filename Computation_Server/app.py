import json

from flask import Flask, request, jsonify
import pandas as pd
import tenseal as ts
import io
import traceback
import base64

app = Flask(__name__)

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


@app.route('/compute-sum', methods=['POST'])
def compute_sum():
    """
    This route is used to compute the sum of encrypted vectors.

    The JSON data should contain the following fields:
    - encrypted_vectors: list of base64-encoded encrypted vectors
    - context: base64-encoded tenseal context
    - number_of_elements: number of elements in the encrypted vectors
    :return:
    """
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
    return jsonify({"sum": serialized_data})


@app.route('/compute-sum-single', methods=['POST'])
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
    app.run(debug=True, port=6000)
