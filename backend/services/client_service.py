from ..models.usuario import Cliente
from ..connection import db
from ..models.servico import Servico
from flask import redirect, url_for

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

def update_client(client_id, data: dict):
    c = Cliente.query.get_or_404(client_id)
    c.nome = data.get('nome', c.nome)
    c.telefone = data.get('telefone', c.telefone)
    c.endereco = data.get('endereco', c.endereco)
    c.cidade = data.get('cidade', c.cidade)
    c.cep = data.get('cep', c.cep)
    c.estado = data.get('estado', c.estado)
    c.cnpj_cpf = data.get('cnpj_cpf', c.cnpj_cpf)
    c.inscricao_estadual = data.get('inscricao_estadual', c.inscricao_estadual)
    c.modelo_veiculo = data.get('modelo_veiculo', c.modelo_veiculo)
    c.placa = data.get('placa', c.placa)
    c.pessoa = data.get('pessoa', c.pessoa)
    c.forma_pagamento = data.get('forma_pagamento', c.forma_pagamento)
    db.session.commit()
    return c

def cliente_excluir(cliente_id):
    cliente = Cliente.query.get(cliente_id)

    # apaga serviços primeiro
    Servico.query.filter_by(cliente_id=cliente.id).delete()

    db.session.delete(cliente)
    db.session.commit()

    return redirect(url_for('main.clientes'))

def get_or_create_anonymous_client():
    c = Cliente.query.filter_by(nome='Cliente não registrado').first()
    if c:
        return c
    c = Cliente(nome='Cliente não registrado')
    db.session.add(c)
    db.session.commit()
    return c
