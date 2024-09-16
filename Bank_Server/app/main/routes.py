from flask import Blueprint, render_template

from database.controller import fetch_all_users

# Create the blueprint for main routes
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    return "Welcome to the Main Page!"


@main_bp.route('/about')
def about():
    return "This is the about page."


@main_bp.route('/users_page')
def users_page():
    return render_template('users.html')


@main_bp.route('/transactions_page')
def transactions_page():
    return render_template('transactions.html')


@main_bp.route('/homomorphic_enc_page')
def display_users():
    all_users = fetch_all_users()


    return render_template('user_statistics.html', users=all_users)


@main_bp.route('/zkp_page')
def zkp_page():
    return render_template('zkp.html')


@main_bp.route('/smpc_page')
def smpc_page():
    return render_template('smpc.html')