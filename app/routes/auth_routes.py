# project/app/auth_routes.py
from flask import Blueprint, request
from werkzeug.security import check_password_hash
from app.models import User
from datetime import timedelta
from flask import jsonify
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, get_jwt
import redis

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        if check_password_hash(user.password, password):
            #token expira apos 60 minutos
            access_token = create_access_token(identity=user.id_user, expires_delta=timedelta(minutes=60))
            return jsonify(access_token=access_token, user_id=user.id_user), 200
        else:
            return jsonify({'error': 'Senha incorreta'}), 401
    else:
        return jsonify({'error': 'E-mail não registado'}), 402

#rota que cria um token apos o existente ter expirado
@auth_routes.route('/refresh_token', methods=['POST'])
@jwt_required()
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)


@auth_routes.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
