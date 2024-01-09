# project/app/models.py
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modelo de user
class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    medicamentos = db.relationship('Medicamento', backref='user', lazy=True)


# Modelo de medicamento
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


# Modelo de historico/administracoes
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


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
