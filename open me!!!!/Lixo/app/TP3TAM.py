from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:rootroot@127.0.0.1:5432/TP3TAM'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta'  # Usada para assinar tokens JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60  # Token expira em 60 minutos

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Modelo de Usuário
class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    medicamentos = db.relationship('Medicamento', backref='user', lazy=True)

# Modelo de Medicamento
class Medicamento(db.Model):
    id_Medicamento = db.Column(db.Integer, primary_key=True)
    nomeMedicamento = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    historicos = db.relationship('Historico', backref='medicamento', lazy=True)

# Modelo de Histórico
class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamento.id_Medicamento'), nullable=False)
    horaAdministracao = db.Column(db.String(255), nullable=False)
    DataAdministracao = db.Column(db.Date, nullable=False)
    quantidade = db.Column(db.Integer)
    administrado = db.Column(db.String(255))
    horaFoitomado = db.Column(db.String(255))

# Rota de registro de usuário
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já registrado'}), 400

    new_user = User(nome=nome, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuário registrado com sucesso'}), 201

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        access_token = create_access_token(identity=user.id_user)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401

# Rota protegida com autenticação JWT para obter medicamentos do usuário logado
@app.route('/medicamentos', methods=['GET'])
@jwt_required()
def get_medicamentos():
    current_user = get_jwt_identity()
    medicamentos = Medicamento.query.filter_by(user_id=current_user).all()
    return jsonify({'medicamentos': [{'id': med.id_Medicamento, 'nome': med.nomeMedicamento, 'descricao': med.descricao} for med in medicamentos]})

# Restante do código permanece o mesmo...

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
