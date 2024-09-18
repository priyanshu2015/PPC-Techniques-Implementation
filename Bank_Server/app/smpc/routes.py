from flask import Blueprint, render_template, request, jsonify
import requests
import secrets
import random
from .shamir_secret_sharing import split_secret, lagrange_interpolate

# Create a Blueprint for the SMPC (Secure Multi-Party Computation) functionality
smpc_bp = Blueprint('smpc', __name__)

# Test route for verifying the blueprint setup
@smpc_bp.route('/test')
def login():
    return "This is the smpc page."

# Initialize global variables for the secret, shares, threshold, and number of shares
secret = None
shares = []
received_shares = []
threshold = 4
num_shares = 6

# Route to split the secret into shares
@smpc_bp.route('/split_info', methods=['GET'])
def split_info():
    global secret, shares, threshold, num_shares
    # Retrieve and set the secret, number of shares, and threshold from query parameters
    secret = int(request.args.get('secret'))
    num_shares = int(request.args.get('num_shares', 6))
    threshold = int(request.args.get('threshold', 4))

    # Split the secret into shares using the provided parameters
    shares = split_secret(secret, num_shares, threshold)

    # Return the secret, coefficients, and generated shares as JSON
    return jsonify({
        "secret": secret,
        "coefficients": [secret] + [random.randint(0, 2**127 - 1) for _ in range(threshold - 1)],
        "shares": shares
    })

# Route to simulate the distribution of shares to bank servers
@smpc_bp.route('/distribution_info', methods=['GET'])
def distribution_info():
    return jsonify({"message": "Shares have been distributed to the bank servers."})

# Route to collect a specified number of shares
@smpc_bp.route('/collect_shares', methods=['GET'])
def collect_shares():
    num = int(request.args.get('num', 0))

    # Check if the requested number of shares exceeds available shares
    if num > len(shares):
        return jsonify({"error": "Requested more shares than available."}), 400

    global received_shares
    # Randomly sample the specified number of shares from the available shares
    received_shares = random.sample(shares, k=num)
    return jsonify({"shares": received_shares})

# Route to reconstruct the secret from collected shares
@smpc_bp.route('/reconstruct_info', methods=['GET'])
def reconstruct_info():
    # Ensure enough shares are available to reconstruct the secret
    if len(received_shares) < threshold:
        return jsonify({"error": "Not enough shares to reconstruct the secret."}), 400

    # Extract x and y values from the collected shares
    x_s, y_s = zip(*received_shares[:threshold])

    # Reconstruct the secret using Lagrange interpolation
    recovered_secret = lagrange_interpolate(0, x_s, y_s, 2 ** 127 - 1)

    # Return the reconstructed secret or an error message if reconstruction fails
    return jsonify({
        "selectedShares": received_shares[:threshold],
        "secret": recovered_secret if recovered_secret == secret else "Reconstruction failed."
    })
