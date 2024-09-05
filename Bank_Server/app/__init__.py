from flask import Flask

# the imports do work but the IDE is not able to resolve them, I dont know why
# maybe because the app is in the folder Bank_Server
from app.main.routes import main_bp
from app.homomorphic_enc.routes import phe_bp
from app.smpc.routes import smpc_bp
from app.zero_knowledge_proof.routes import zkp_bp
from app.data.routes import data_bp


def create_app():
    app = Flask(__name__)

    # Configuration can be loaded here
    app.config.from_object('config.Config')

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(phe_bp, url_prefix='/phe')
    app.register_blueprint(smpc_bp, url_prefix='/smpc')
    app.register_blueprint(zkp_bp, url_prefix='/zkp')
    app.register_blueprint(data_bp, url_prefix='/data')

    return app