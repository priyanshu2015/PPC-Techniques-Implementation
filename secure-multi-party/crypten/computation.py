import os

from flask import Flask, request, jsonify
import crypten
import torch

app = Flask(__name__)

# Initialize CrypTen
# check if os is windows
if os.name == 'nt':
    crypten.init_thread(0, 1)
else:
    crypten.init()

# Store received tensors
received_tensors = {}

def load_files():
    for party in ['bank1', 'bank2']:
        file_path = f'server/encrypted_data_{party}.pth'
        if not os.path.exists(file_path):
            continue
        received_tensors[party] = torch.load(file_path)

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
    print("Computing...")
    # Assuming all data is received
    crypten.init_thread(0, 1)
    result = received_tensors['bank1'] > received_tensors['bank2']
    plain = received_tensors['bank1'].get_plain_text()
    print(f"bank1's data: {plain}")
    result = result.reveal()
    if result.item():
        return jsonify({"message": "bank1's data is greater than bank2's data."})
    else:
        return jsonify({"message": "bank1's data is not greater than bank2's data."})


def test():
    if 'bank1' not in received_tensors or 'bank2' not in received_tensors:
        return
    plain = received_tensors['bank1'].get_plain_text()
    print(f"bank1's data: {plain}")


if __name__ == '__main__':
    print("Starting server...")
    load_files()
    test()
    app.run(debug=True, host="0.0.0.0")
