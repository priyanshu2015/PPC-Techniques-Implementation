from time import perf_counter

from flask import Blueprint, render_template, jsonify
import requests
import base64
import json
import tenseal as ts


from .homomorphic_encryption import (
    encrypt_vector_for_sum,
    serialize_encrypted_vector,
    serialize_encrypted_vectors,
    convert_flot_to_int,
    deserialize_encrypted_vector,
    deserialize_encrypted_vectors,
    convert_int_to_float,
    get_serialized_context
)

from database.controller import fetch_transactions_by_userid

"""
This file contains the routes for the Homomorphic Encryption page.
"""


phe_bp = Blueprint('phe', __name__)

COMPUTATION_SERVER_URL = "http://localhost:5500/api"


@phe_bp.route('/transaction_sum/<int:userid>', methods=['GET'])
def request_transaction_sum(userid):
    """
    This function fetches the transactions for a user and calculates the sum of the amounts by sending the encrypted
    amounts to the computation server
    :param userid:
    :return: sum of the transactions
    """
    start = perf_counter()

    transactions = fetch_transactions_by_userid(userid)
    if not transactions:
        return jsonify({"error": "No transactions found for user"}), 404

    # extract the amounts from the transactions and multiply by 100 to convert to int
    amounts = [convert_flot_to_int(transaction['amount']) for transaction in transactions]

    # encrypt and base64 encode the amounts
    encrypted_vector, number_of_elements = encrypt_vector_for_sum(amounts)

    """
    #------------------------------------
    # Theoretical sum
    deserialized_vectors = deserialize_encrypted_vectors(serialized_encrypted_vectors)
    encrypted_sum2 = deserialized_vectors[0].sum()
    for s in deserialized_vectors[1:]:
        encrypted_sum2 += s.sum()

    serialized_datas = serialize_encrypted_vector(encrypted_sum2)
    decrypted_sum2 = encrypted_sum2.decrypt()
    print(f"Decrypted real sum: {decrypted_sum2[0]}")
    # ------------------------------------
    """

    encrypted_sum = request_encrypted_sum(encrypted_vector, number_of_elements)

    decrypted_sum = encrypted_sum.decrypt()
    print("Decrypted sum: ", decrypted_sum[0])
    real_sum = convert_int_to_float(decrypted_sum[0])
    print("Sum: ", real_sum)
    end = perf_counter()
    print(f"Time taken: {end - start} seconds")
    return jsonify(real_sum), 200


def request_encrypted_sum(encrypted_vector, number_of_elements) -> ts.bfv_vector:
    """
    This function is a helper function that sends the encrypted vector to the computation server to calculate the sum
    :param encrypted_vector:
    :param number_of_elements:
    :return: sum of the encrypted vector
    """
    headers = {'Content-Type': 'application/json'}
    url = f"{COMPUTATION_SERVER_URL}/compute-sum"

    serialized_encrypted_vectors = serialize_encrypted_vectors(encrypted_vector)
    print(f"Size of Context in bytes: {len(get_serialized_context().encode('utf-8'))}")
    print(f"Size of Encrypted Vectors in bytes: {sum([len(v.encode('utf-8')) for v in serialized_encrypted_vectors])}")

    data = {
        "context": get_serialized_context(),
        "number_of_elements": number_of_elements,
        "encrypted_vectors": serialized_encrypted_vectors.copy()
    }
    json_data = json.dumps(data)

    size_in_bytes = len(json_data.encode('utf-8'))
    print(f"Size of json_data in bytes: {size_in_bytes}")

    # Send the POST request with the byte array as the body
    response = requests.post(url, data=json_data, headers=headers)

    if response.status_code != 200:
        print(f"Failed to get response from computation server. Status code: {response.status_code}")
        raise Exception("Error in request_encrypted_sum")

    response_data = response.json()
    serialized_encrypted_sum = response_data['sum']
    encrypted_sum = deserialize_encrypted_vector(serialized_encrypted_sum)
    return encrypted_sum
