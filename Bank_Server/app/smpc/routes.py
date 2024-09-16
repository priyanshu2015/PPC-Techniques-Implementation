from flask import Blueprint, render_template, request, jsonify

import requests
import secrets
import random
from .shamir_secret_sharing import split_secret, lagrange_interpolate


smpc_bp = Blueprint('smpc', __name__)


@smpc_bp.route('/test')
def login():
    return "This is the smpc page."

# Initialize variables
secret = None
shares = []
received_shares = []
threshold = 4
num_shares = 6


@smpc_bp.route('/split_info', methods=['GET'])
def split_info():
    global secret, shares, threshold, num_shares
    secret = int(request.args.get('secret'))
    num_shares = int(request.args.get('num_shares', 6))
    threshold = int(request.args.get('threshold', 4))
    shares = split_secret(secret, num_shares, threshold)
    return jsonify({
        "secret": secret,
        "coefficients": [secret] + [random.randint(0, 2**127 - 1) for _ in range(threshold - 1)],
        "shares": shares
    })


@smpc_bp.route('/distribution_info', methods=['GET'])
def distribution_info():
    return jsonify({"message": "Shares have been distributed to the bank servers."})


@smpc_bp.route('/collect_shares', methods=['GET'])
def collect_shares():
    num = int(request.args.get('num', 0))
    if num > len(shares):
        return jsonify({"error": "Requested more shares than available."}), 400
    global received_shares
    received_shares = random.sample(shares, k=num)
    return jsonify({"shares": received_shares})


@smpc_bp.route('/reconstruct_info', methods=['GET'])
def reconstruct_info():
    if len(received_shares) < threshold:
        return jsonify({"error": "Not enough shares to reconstruct the secret."}), 400

    x_s, y_s = zip(*received_shares[:threshold])
    recovered_secret = lagrange_interpolate(0, x_s, y_s, 2 ** 127 - 1)

    return jsonify({
        "selectedShares": received_shares[:threshold],
        "secret": recovered_secret if recovered_secret == secret else "Reconstruction failed."
    })