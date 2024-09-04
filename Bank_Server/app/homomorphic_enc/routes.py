from flask import Blueprint, render_template

phe_bp = Blueprint('phe', __name__)


@phe_bp.route('/test')
def login():
    return "This is the Homomorphic-Encryption-Page."

