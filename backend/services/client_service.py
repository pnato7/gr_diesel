from ..models.usuario import Cliente
from ..connection import db

def list_clients():
    return Cliente.query.order_by(Cliente.created_at.desc()).all()

def get_client(client_id):
    return Cliente.query.get_or_404(client_id)

def create_client(data: dict):
    c = Cliente(
        nome=data.get('nome'),
        telefone=data.get('telefone'),
        endereco=data.get('endereco'),
        cidade=data.get('cidade'),
        cep=data.get('cep'),
        estado=data.get('estado'),
        cnpj_cpf=data.get('cnpj_cpf'),
        inscricao_estadual=data.get('inscricao_estadual'),
        modelo_veiculo=data.get('modelo_veiculo'),
        placa=data.get('placa'),
        pessoa=data.get('pessoa'),
        forma_pagamento=data.get('forma_pagamento')
    )
    db.session.add(c)
    db.session.commit()
    return c


def get_or_create_anonymous_client():
    c = Cliente.query.filter_by(nome='Cliente não registrado').first()
    if c:
        return c
    c = Cliente(nome='Cliente não registrado')
    db.session.add(c)
    db.session.commit()
    return c
