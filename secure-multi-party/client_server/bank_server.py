# bank_server.py
from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

# Store for the bank's share
share = None

@app.route('/receive_share', methods=['POST'])
def receive_share():
    global share
    share = request.json['share']
    return jsonify({"message": "Share received."})

@app.route('/fetch_share', methods=['GET'])
def fetch_share():
    if share is None:
        return jsonify({"error": "No share available."}), 404
    return jsonify({'share': share})

if __name__ == '__main__':
    port = int(sys.argv[1])  # Port passed as argument
    app.run(debug=True, port=port)
