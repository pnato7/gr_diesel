from datetime import datetime
from backend.db import db


class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(50))
    endereco = db.Column(db.String(250))
    cidade = db.Column(db.String(100))
    cep = db.Column(db.String(30))
    estado = db.Column(db.String(50))
    cnpj_cpf = db.Column(db.String(80))
    inscricao_estadual = db.Column(db.String(80))
    modelo_veiculo = db.Column(db.String(100))
    placa = db.Column(db.String(20))
    pessoa = db.Column(db.String(50))  # PF ou CNPJ
    forma_pagamento = db.Column(db.String(50))  # Pix, dinheiro, debito, credito
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Cliente {self.nome}>"


class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    descricao = db.Column(db.Text)  # qual parte do veículo precisa de reforma
    data_emissao = db.Column(db.DateTime)
    teste_bico = db.Column(db.Boolean, default=False)
    teste_bomba = db.Column(db.Boolean, default=False)
    apenas_teste = db.Column(db.Boolean, default=False)
    mao_de_obra = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship('Cliente', backref=db.backref('servicos', lazy=True))


class Peca(db.Model):
    __tablename__ = 'pecas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    unidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Float, default=0.0)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'))

    servico = db.relationship('Servico', backref=db.backref('pecas', lazy=True))

    @property
    def valor_total(self):
        return (self.unidade or 0) * (self.valor_unitario or 0.0)


class NotaServico(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    total_pecas = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    servico = db.relationship('Servico', backref=db.backref('nota', uselist=False))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hash
    is_owner = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"
