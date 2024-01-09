# project/app/routes/medicamento_routes.py

from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from ..models import Medicamento, db, Administracao

medicamento_routes = Blueprint('medicamento_routes', __name__)

# adicionar um novo medicamento
@medicamento_routes.route('/adicionar_medicamentos', methods=['POST'])
@jwt_required()
def adicionar_medicamento():
    current_user = get_jwt_identity()
    dados_medicamento = request.get_json()
    if Medicamento.query.filter_by(user_id=current_user, nomeMedicamento=dados_medicamento['nomeMedicamento']).first():
        return jsonify({'error': 'Nome de medicamento já existe para este utilizador!'}), 400
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

# obter os medicamentos
@medicamento_routes.route('/obter_medicamentos', methods=['GET'])
@jwt_required()
def get_medicamentos():
    try:
        current_user = get_jwt_identity()
        medicamentos = Medicamento.query.filter_by(user_id=current_user).all()

        response_data = {
            'medicamentos': [
                {
                    'id': med.id_Medicamento,
                    'nome': med.nomeMedicamento,
                    'dosagem': med.dosagem,
                    'data': med.Data.strftime('%Y-%m-%d'),
                    'forma': med.formaFarmaceutica,
                    'posologia': med.posologia,
                    'horarios': med.horarios,
                    'quantidade': med.quantidade,
                    'duracao': med.duracao,
                    'id_user': med.user_id
                } for med in medicamentos
            ]
        }

        # resposta com código 200 de sucesso
        return make_response(jsonify(response_data), 200)

    except Exception as e:
        # resposta de erro com código 500 (Internal Server Error)
        return make_response(jsonify({'error': str(e)}), 500)


# remover um medicamento e administrações associadas
@medicamento_routes.route('/remover_medicamento', methods=['PUT'])
@jwt_required()
def remover_medicamento():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        id_medicamento = data.get('id_medicamento')

        # verificar se medicamento pertence ao user logado
        medicamento = Medicamento.query.filter_by(id_Medicamento=id_medicamento, user_id=current_user).first()

        if not medicamento:
            return jsonify({'error': 'Medicamento não encontrado ou não autorizado'}), 404

        # verificar e remover administrações não administradas associadas ao medicamento
        administracoes_nao_administradas = Administracao.query.filter_by(medicamento_id=id_medicamento).all()
        for administracao in administracoes_nao_administradas:
            db.session.delete(administracao)

        # commit na tabela de administrações antes de remover medicamento
        db.session.commit()

        db.session.delete(medicamento)
        db.session.commit()

        return jsonify({'message': 'Medicamento removido com sucesso'}), 200
    except Exception as e:
        db.session.rollback()  # operações na bd nao se realizam em caso de erro
        return jsonify({'error': f'Erro ao remover medicamento: {str(e)}'}), 500


# alterar medicamento
@medicamento_routes.route('/alterar_medicamento', methods=['PUT'])
@jwt_required()
def alterar_medicamento():
    try:
        current_user = get_jwt_identity()
        dados_medicamento = request.get_json()
        id_medicamento = dados_medicamento.get('id_medicamento')
        medicamento = Medicamento.query.filter_by(id_Medicamento=id_medicamento, user_id=current_user).first()

        if not medicamento:
            return jsonify({'error': 'Medicamento não encontrado..'}), 404

        # verificar se nome do medicamento ja existe
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

        # remover administrações não administradas associadas
        Administracao.query.filter_by(medicamento_id=id_medicamento).delete()
        db.session.commit()

        return jsonify({'message': 'Medicamento alterado com sucesso'}), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao alterar medicamento: {str(e)}'}), 500
