from ..connection import db
from datetime import datetime

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
