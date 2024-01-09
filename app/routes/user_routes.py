# project/app/user_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from app.models import User, db
user_routes = Blueprint('user_routes', __name__)


# registar utilizador
@user_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já registado na aplicação..'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(nome=nome, email=email, password=hashed_password)
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({'message': 'Utilizador registado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao registar utilizador..', 'details': str(e)}), 500

# apresentar dados de utilizador
@user_routes.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if user:
        user_data = {
            'nome': user.nome,
            'email': user.email,
        }

        return jsonify(user_data), 200
    else:
        return jsonify({'error': 'Utilizador não encontrado'}), 404
