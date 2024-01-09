# project/app/routes/administracao_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from sqlalchemy import inspect

from ..models import Administracao, Medicamento, db

administracao_routes = Blueprint('administracao_routes', __name__)

# adicionar administracoes
@administracao_routes.route('/adicionar_administracao', methods=['POST'])
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
                    # verificar se já existe administração para medicamento, horário e data específicos
                    administracao_existente = Administracao.query.filter_by(
                        nomeMedicamento=medicamento.nomeMedicamento,
                        horaAdministracao=horario,
                        formaFarmaceutica=medicamento.formaFarmaceutica,
                        DataAdministracao=data_atual_string,
                        quantidade=medicamento.quantidade,
                        medicamento_id=medicamento.id_Medicamento
                    ).first()

                    if not administracao_existente:
                        # adiciona administracao caso nao exista
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

        # commit apos adicionar administracao
        if administracoes_adicionadas:
            db.session.commit()
            return jsonify({'message': 'Administrações adicionadas com sucesso'}), 201
        else:
            return jsonify({'message': 'Nenhum medicamento corresponde à data atual ou administrações já existem'}), 400

    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar administrações: {str(e)}'}), 500

# obter administracoes do user autenticado
@administracao_routes.route('/obter_administracoes', methods=['GET'])
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

# rota para alterar o estado e hora de administração
@administracao_routes.route('/alterar_estado_hora_administracao', methods=['PUT'])
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