from flask import Flask, request, jsonify
import torch as th
import syft as sy


app = Flask(__name__)

# Create a hook for PyTorch
hook = sy.TorchHook(th)

# Store shares from Alice and Bob
shares = {}

@app.route('/receive_share', methods=['POST'])
def receive_share():
    data = request.get_json()
    worker_id = data['worker_id']
    share = sy.tensor(data['share']).send(worker_id)
    shares[worker_id] = share
    return jsonify({'status': 'Share received'})

@app.route('/compute', methods=['POST'])
def compute():
    if 'alice' in shares and 'bob' in shares:
        result = shares['alice'] + shares['bob']
        return jsonify({'result': result.get().tolist()})
    return jsonify({'status': 'Shares missing'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)