# app/app.py
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.models import db,TokenBlocklist
from datetime import datetime, timedelta
from .routes import create_routes
def create_app():
    app = Flask(__name__)
    # inicializar JWTManager
    CORS(app)
    # dados de acesso à bd
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:rootroot@127.0.0.1:5432/TP3TAM'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'TAM3TP_MUAIAD'
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    jwt=JWTManager(app)

    db.init_app(app)
    # Use the create_routes function to register routes
    auth_blueprint, user_blueprint, medicamento_blueprint, administracao_blueprint = create_routes()

    # Register the blueprints with the app
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(medicamento_blueprint)
    app.register_blueprint(administracao_blueprint)

    # Configure the logging in your application
    logging.basicConfig(level=logging.DEBUG)

    # Example logs in your code
    app.logger.debug("Token gerado com sucesso!")
    app.logger.debug(f"Current date and time: {datetime.now()}")

    with app.app_context():
        db.create_all()

    return app