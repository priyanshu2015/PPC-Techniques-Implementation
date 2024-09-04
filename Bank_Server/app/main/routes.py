from flask import Blueprint

# Create the blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return "Welcome to the Main Page!"

@main_bp.route('/about')
def about():
    return "This is the about page."