import sqlite3
from flask import Flask
from flask import jsonify, Blueprint, request

from database.controller import (
    fetch_all_users,
    fetch_all_transactions,
    fetch_user_by_id,
    fetch_transaction_by_id,
    fetch_transactions_by_userid
)

data_bp = Blueprint('data', __name__)

# Route to get all users
@data_bp.route('/users', methods=['GET'])
def get_users():
    users_list = fetch_all_users()
    return jsonify(users_list), 200

# Route to get a specific user by userid
@data_bp.route('/users/<int:userid>', methods=['GET'])
def get_user(userid):
    user = fetch_user_by_id(userid)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404

# Route to get all transactions
@data_bp.route('/transactions', methods=['GET'])
def get_transactions():
    transactions_list = fetch_all_transactions()
    return jsonify(transactions_list), 200

# Route to get a specific transaction by transactionid
@data_bp.route('/transactions/<int:transactionid>', methods=['GET'])
def get_transaction(transactionid):
    transaction = fetch_transaction_by_id(transactionid)
    if transaction:
        return jsonify(transaction), 200
    else:
        return jsonify({"error": "Transaction not found"}), 404

# Route to get all transactions for a specific user by userid
@data_bp.route('/users/<int:userid>/transactions', methods=['GET'])
def get_transactions_for_user(userid):
    transactions = fetch_transactions_by_userid(userid)
    if transactions:
        return jsonify(transactions), 200
    else:
        return jsonify({"error": "No transactions found for user"}), 404

