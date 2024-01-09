# project/app/routes/__init__.py
from flask import Blueprint

#imports dos route modules
from .auth_routes import auth_routes
from .user_routes import user_routes
from .medicamento_routes import medicamento_routes
from .administracao_routes import administracao_routes


def create_routes():
    # criar um blueprint para cada route module
    auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
    user_blueprint = Blueprint('user', __name__, url_prefix='/user')
    medicamento_blueprint = Blueprint('medicamento', __name__, url_prefix='/medicamento')
    administracao_blueprint = Blueprint('administracao', __name__, url_prefix='/administracao')

    # registar as routes de cada module para o blueprint correspondente
    auth_blueprint.register_blueprint(auth_routes)
    user_blueprint.register_blueprint(user_routes)
    medicamento_blueprint.register_blueprint(medicamento_routes)
    administracao_blueprint.register_blueprint(administracao_routes)

    # retornar blueprints
    return auth_blueprint, user_blueprint, medicamento_blueprint, administracao_blueprint
