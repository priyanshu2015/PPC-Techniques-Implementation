from flask import Flask, request, jsonify
import requests
from schnorr_core import ZK, ZKSignature, ZKData
import base64

app = Flask(__name__)

server_password = "SecretServerPassword"
server_zk = ZK.new(curve_name="secp384r1", hash_alg="sha3_512")
server_signature: ZKSignature = server_zk.create_signature("SecureServerPassword")
client_signature = None


@app.route('/login', methods=['POST'])
def login():
    global server_password
    global client_signature
    global client_zk

    try:
        print(request.json.get("signature"))
    except Exception as e:
        pass

    signature = request.json.get("signature")

    client_signature = ZKSignature.from_json(signature)

    client_zk = ZK(client_signature.params)

    # print(client_zk.token())

    token = server_zk.sign("SecureServerPassword", client_zk.token)

    token = token.to_json()

    return jsonify({"token": token})


@app.route('/compute', methods=['POST'])
def compute():
    global server_signature
    global client_signature
    global server_zk

    proof = request.json.get("proof")
    proof = ZKData.from_json(proof)
    token = ZKData.from_json(proof.data)

    if not server_zk.verify(token, server_signature):
        return jsonify({"error": "Invalid proof"}), 400
    else:
        if not client_zk.verify(proof, client_signature, data=token):
            return jsonify({"error": "Invalid proof"}), 400

    return jsonify({"message": "Computations successful"})


if __name__ == '__main__':
    app.run(debug=True, port=6000)