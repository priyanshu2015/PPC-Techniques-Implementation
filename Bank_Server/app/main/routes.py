from flask import Blueprint, render_template

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