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
        modelo_veiculo=data.get('modelo_veiculo'),
        placa=data.get('placa'),
        pessoa=data.get('pessoa'),
        forma_pagamento=data.get('forma_pagamento')
    )
    db.session.add(c)
    db.session.commit()
    return c
