from flask import Blueprint, render_template, jsonify
import requests
import base64
import json
import tenseal as ts


POLY_MODULUS_DEGREE = 4096
# Setup TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.BFV,
    poly_modulus_degree=POLY_MODULUS_DEGREE,
    plain_modulus=1032193
    #plain_modulus=4294967295,
)
context.generate_galois_keys()


"""
import app.homomorphic_enc.homomorphic_encryption
from app.homomorphic_enc.homomorphic_encryption import (
    encrypt_vector_for_sum,
    serialize_encrypted_vector,
    serialize_encrypted_vectors,
    convert_flot_to_int,
    deserialize_encrypted_vector,
    deserialize_encrypted_vectors,
    convert_int_to_float
)

from database.controller import fetch_transactions_by_userid

def request_encrypted_sum(serialized_encrypted_vectors, number_of_elements) -> ts.bfv_vector:
    headers = {'Content-Type': 'application/json'}
    url = "http://localhost:6000/compute-sum"

    data = {
        "number_of_elements": number_of_elements,
        "encrypted_vectors": serialized_encrypted_vectors.copy()
    }
    json_data = json.dumps(data)
    # Send the POST request with the byte array as the body
    response = requests.post(url, data=json_data, headers=headers)

    if response.status_code != 200:
        raise Exception("Error in request_encrypted_sum")

    response_data = response.json()
    serialized_encrypted_sum = response_data['sum']
    return serialized_encrypted_sum



# extract the amounts from the transactions and multiply by 100 to convert to int
amounts = [1, 2, 3, 4]

# encrypt and base64 encode the amounts
encrypted_vector, number_of_elements = encrypt_vector_for_sum(amounts)
serialized_encrypted_vectors = serialize_encrypted_vectors(encrypted_vector)

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

print("Serialized encrypted vectors")

serialized_encrypted_sum = request_encrypted_sum(serialized_encrypted_vectors, number_of_elements)
print(f"Same: {serialized_encrypted_sum == serialized_datas}")

encrypted_sum = deserialize_encrypted_vector(serialized_encrypted_sum)

decrypted_sum = encrypted_sum.decrypt()
print("Decrypted sum: ", decrypted_sum[0])
real_sum = convert_int_to_float(decrypted_sum[0])
print("Sum: ", real_sum)
"""
#---------------------------------------------------------------------------

# Create BSV encrypted vector
vector = [1, 2, 3, 4, 5]  # example vector
encrypted_bsv = ts.bfv_vector(context, vector)

# Serialize the vector to bytes
bsv_serialized = encrypted_bsv.serialize()

# Encode the bytes to base64 for JSON compatibility
bsv_encoded = base64.b64encode(bsv_serialized).decode('utf-8')

context_serialized = context.serialize(save_public_key=True, save_secret_key=False, save_galois_keys=True)
context_encoded = base64.b64encode(context_serialized).decode('utf-8')

data = {
    'context': context_encoded,
    'bsv_vector': bsv_encoded
}

# Pack the encoded data in JSON
json_payload = json.dumps(data)

# Send the JSON payload via a POST request
url = 'http://localhost:6000/compute-sum-single'
response = requests.post(url, json=json_payload)

sum_json = response.json()

# Decode the base64 result back to bytes
result_encoded = sum_json['sum']
result_serialized = base64.b64decode(result_encoded)

# Deserialize the result
sum_encrypted = ts.bfv_vector_from(context, result_serialized)

# Decrypt the result
sum_result = sum_encrypted.decrypt()

print(f"The sum of the vector is: {sum_result}")