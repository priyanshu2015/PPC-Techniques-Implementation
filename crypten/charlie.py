from flask import Flask, request, jsonify
import crypten
import torch

app = Flask(__name__)

# Initialize CrypTen
crypten.init()

# Store received tensors
received_tensors = {}

@app.route('/upload/<string:party>', methods=['POST'])
def receive_data(party):
    print(f"Received data from {party}.")
    file = request.files['file']
    file_path = f'server/encrypted_data_{party}.pth'
    file.save(file_path)
    received_tensors[party] = torch.load(file_path)
    return jsonify({"message": f"{party}'s data received and loaded."})

@app.route('/compute', methods=['GET'])
def compute():
    # Assuming all data is received
    result = received_tensors['alice'] > received_tensors['bob']
    result = result.reveal()
    if result.item():
        return jsonify({"message": "Alice's data is greater than Bob's data."})
    else:
        return jsonify({"message": "Alice's data is not greater than Bob's data."})



if __name__ == '__main__':
    app.run(debug=True)
