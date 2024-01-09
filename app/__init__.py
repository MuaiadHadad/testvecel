# project/app/__init__.py
from flask import Flask
from .routes import create_routes


def create_app():
    app = Flask(__name__)
    return app
