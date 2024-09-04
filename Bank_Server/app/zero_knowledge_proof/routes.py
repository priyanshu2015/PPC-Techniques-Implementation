from flask import Blueprint, render_template

zkp_bp = Blueprint('zkp', __name__)


@zkp_bp.route('/test')
def login():
    return "This is the Zero-Knowledge-Proof page."

