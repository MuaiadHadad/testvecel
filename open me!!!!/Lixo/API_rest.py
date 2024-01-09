from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:rootroot@127.0.0.1:5432/TP3TAM'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'TAM3TP_MUAIAD'  # Usada para assinar tokens JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)  # Exemplo de configuração para 60 minutos

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
    dosagem = db.Column(db.String(255))
    formaFarmaceutica = db.Column(db.String(255))
    posologia = db.Column(db.String(255))
    horarios = db.Column(db.String(255))
    quantidade = db.Column(db.Integer)
    duracao = db.Column(db.String(255))
    Data = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)


# Modelo de Histórico
class Administracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamento.id_Medicamento'), nullable=False)
    nomeMedicamento = db.Column(db.String(255))
    formaFarmaceutica = db.Column(db.String(255))
    horaAdministracao = db.Column(db.String(255))
    DataAdministracao = db.Column(db.Date)
    quantidade = db.Column(db.Integer)
    administrado = db.Column(db.Boolean)
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

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(nome=nome, email=email, password=hashed_password)
    db.session.add(new_user)

    try:
        db.session.commit()
        return jsonify({'message': 'Usuário registrado com sucesso'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao registrar usuário', 'details': str(e)}), 500


# Rota de login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id_user, expires_delta=timedelta(minutes=60))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401


# Rota para adicionar um novo medicamento
@app.route('/medicamentos', methods=['POST'])
@jwt_required()
def adicionar_medicamento():
    current_user = get_jwt_identity()
    dados_medicamento = request.get_json()
    if Medicamento.query.filter_by(user_id=current_user, nomeMedicamento=dados_medicamento['nomeMedicamento']).first():
        return jsonify({'error': 'Nome de medicamento já existe para este usuário'}), 400
    novo_medicamento = Medicamento(
        nomeMedicamento=dados_medicamento['nomeMedicamento'],
        dosagem=dados_medicamento['dosagem'],
        formaFarmaceutica=dados_medicamento['formaFarmaceutica'],
        posologia=dados_medicamento['posologia'],
        horarios=dados_medicamento['horarios'],
        quantidade=dados_medicamento['quantidade'],
        duracao=dados_medicamento['duracao'],
        Data=dados_medicamento['date'],
        user_id=current_user
    )

    db.session.add(novo_medicamento)
    db.session.commit()

    return jsonify({'message': 'Medicamento adicionado com sucesso'}), 201

# Rota para buscar os medicamentos
@app.route('/medicamentos', methods=['GET'])
@jwt_required()
def get_medicamentos():
    current_user = get_jwt_identity()
    medicamentos = Medicamento.query.filter_by(user_id=current_user).all()
    return jsonify({
        'medicamentos': [
            {
                'id': med.id_Medicamento,
                'nome': med.nomeMedicamento,
                'dosagem': med.dosagem,
                'data': med.Data.strftime('%Y-%m-%d')
            } for med in medicamentos
        ]
    })


# Rota para adicionar administrações
@app.route('/adicionar_administracao', methods=['POST'])
@jwt_required()
def adicionar_administracao():
    current_user = get_jwt_identity()
    try:
        medicamentos = Medicamento.query.filter_by(user_id=current_user).all()

        if not medicamentos:
            return jsonify({'error': 'Medicamento não encontrado'}), 404
        data_atual = datetime.now().strftime('%Y-%m-%d')
        administracoes_adicionadas = False

        for medicamento in medicamentos:
            data_atual_string = medicamento.Data.strftime('%Y-%m-%d')
            if data_atual_string == data_atual:
                for horario in medicamento.horarios.split(','):
                    # Verifica se já existe administração para o medicamento, horário e data específicos
                    administracao_existente = Administracao.query.filter_by(
                        nomeMedicamento=medicamento.nomeMedicamento,
                        horaAdministracao=horario,
                        formaFarmaceutica=medicamento.formaFarmaceutica,
                        DataAdministracao=data_atual_string,
                        quantidade=medicamento.quantidade,
                        medicamento_id=medicamento.id_Medicamento
                    ).first()

                    if not administracao_existente:
                        # Adiciona a administração apenas se não existir
                        nova_administracao = Administracao(
                            nomeMedicamento=medicamento.nomeMedicamento,
                            horaAdministracao=horario,
                            formaFarmaceutica=medicamento.formaFarmaceutica,
                            DataAdministracao=data_atual_string,
                            quantidade=medicamento.quantidade,
                            administrado=False,
                            horaFoitomado="00",
                            medicamento_id=medicamento.id_Medicamento
                        )

                        db.session.add(nova_administracao)
                        administracoes_adicionadas = True

        # Fora do loop, faça o commit apenas se administrações foram adicionadas
        if administracoes_adicionadas:
            db.session.commit()
            return jsonify({'message': 'Administrações adicionadas com sucesso'}), 201
        else:
            return jsonify({'message': 'Nenhum medicamento corresponde à data atual ou administrações já existem'}), 400

    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar administrações: {str(e)}'}), 500


# Rota para obter administrações do usuário autenticado
@app.route('/administracoes', methods=['GET'])
@jwt_required()
def get_administracoes():
    current_user = get_jwt_identity()
    administracoes = Administracao.query.join(Medicamento).filter(Medicamento.user_id == current_user).all()
    result = []

    for administracao in administracoes:
        admin_dict = {}
        for col in inspect(administracao).mapper.column_attrs:
            admin_dict[col.key] = getattr(administracao, col.key)
            if isinstance(admin_dict[col.key], datetime):
                admin_dict[col.key] = admin_dict[col.key].strftime('%Y-%m-%d')

        result.append(admin_dict)

    return jsonify({'administracoes': result})


# rota para alterar o estado e a hora de administração
@app.route('/alterar_estado_hora_administracao', methods=['PUT'])
@jwt_required()
def alterar_estado_hora_administracao():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        hora = data.get('hora')
        id_data = data.get('id')

        administracao = Administracao.query.join(Medicamento).filter(Administracao.id == id_data,
                                                                     Medicamento.user_id == current_user).first()
        if not administracao:
            return jsonify({'error': 'Administração não encontrada ou não autorizada'}), 404

        administracao.horaFoitomado = hora
        administracao.administrado = True

        db.session.commit()

        return jsonify({'message': 'Estado e hora de administração alterados com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao alterar estado e hora de administração: {str(e)}'}), 500


# Rota para remover um medicamento e administrações associadas
@app.route('/remover_medicamento', methods=['DELETE'])
@jwt_required()
def remover_medicamento():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        id_medicamento = data.get('id_medicamento')

        # Verificar se o medicamento pertence ao usuário atual
        medicamento = Medicamento.query.filter_by(id_Medicamento=id_medicamento, user_id=current_user).first()

        if not medicamento:
            return jsonify({'error': 'Medicamento não encontrado ou não autorizado'}), 404

        # Verificar e remover administrações não administradas associadas ao medicamento
        administracoes_nao_administradas = Administracao.query.filter_by(medicamento_id=id_medicamento).all()
        for administracao in administracoes_nao_administradas:
            db.session.delete(administracao)

        # Commit as alterações na tabela de administração antes de excluir o medicamento
        db.session.commit()

        # Remover o medicamento
        db.session.delete(medicamento)
        db.session.commit()

        return jsonify({'message': 'Medicamento removido com sucesso'}), 200
    except Exception as e:
        db.session.rollback()  # Desfaz as alterações em caso de erro
        return jsonify({'error': f'Erro ao remover medicamento: {str(e)}'}), 500

# Rota para alterar um medicamento
@app.route('/alterar_medicamento', methods=['PUT'])
@jwt_required()
def alterar_medicamento():
    try:
        current_user = get_jwt_identity()
        dados_medicamento = request.get_json()
        id_medicamento = dados_medicamento.get('id_medicamento')
        medicamento = Medicamento.query.filter_by(id_Medicamento=id_medicamento, user_id=current_user).first()

        if not medicamento:
            return jsonify({'error': 'Medicamento não encontrado'}), 404

        # Verifique se o novo nome já existe com outro ID
        if Medicamento.query.filter(Medicamento.nomeMedicamento == dados_medicamento['nomeMedicamento'],
                                    Medicamento.id_Medicamento != id_medicamento,
                                    Medicamento.user_id == current_user).first():
            return jsonify({'error': 'Já existe um medicamento com este nome'}), 400

        medicamento.nomeMedicamento = dados_medicamento['nomeMedicamento']
        medicamento.dosagem = dados_medicamento['dosagem']
        medicamento.formaFarmaceutica = dados_medicamento['formaFarmaceutica']
        medicamento.posologia = dados_medicamento['posologia']
        medicamento.horarios = dados_medicamento['horarios']
        medicamento.quantidade = dados_medicamento['quantidade']
        medicamento.duracao = dados_medicamento['duracao']
        medicamento.Data = dados_medicamento['date']

        db.session.commit()

        # Remover administrações não administradas associadas
        # Administracao.query.filter_by(medicamento_id=id, administrado=False).delete()
        # db.session.commit()

        return jsonify({'message': 'Medicamento alterado com sucesso'}), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao alterar medicamento: {str(e)}'}), 500


# Configure o logging no seu aplicativo
logging.basicConfig(level=logging.DEBUG)

# Exemplo de logs no seu código
app.logger.debug("Token gerado com sucesso")
app.logger.debug(f"Data e hora atual: {datetime.now()}")
# Criar as tabelas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
