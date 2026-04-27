from ..models.servico import Servico, Peca
from ..models.agendamento import NotaServico
from ..connection import db
from flask import Blueprint, send_file, jsonify
from backend.utils.gerar_nota_png import gerar_nota_png
import os

def get_latest_services(limit=20):
    return Servico.query.order_by(Servico.created_at.desc()).limit(limit).all()

def create_service(cliente_id, data: dict, pecas: list):
    servico = Servico(
        cliente_id=cliente_id,
        descricao=data.get('descricao'),
        teste_bico=bool(data.get('teste_bico')),
        teste_bomba=bool(data.get('teste_bomba')),
        apenas_teste=bool(data.get('apenas_teste')),
        mao_de_obra=float(data.get('mao_de_obra') or 0.0)
    )
    db.session.add(servico)
    db.session.commit()

    total_pecas = 0.0
    for p in pecas:
        item = Peca(nome=p['nome'], unidade=p['unidade'], valor_unitario=p['valor_unitario'], servico_id=servico.id)
        db.session.add(item)
        total_pecas += item.valor_total

    nota = NotaServico(servico_id=servico.id, total_pecas=total_pecas, total=total_pecas + servico.mao_de_obra)
    db.session.add(nota)
    db.session.commit()
    return servico

def get_service(servico_id):
    return Servico.query.get_or_404(servico_id)

def update_service(servico_id, cliente_id, data: dict, pecas: list):
    servico = Servico.query.get_or_404(servico_id)
    servico.cliente_id = cliente_id
    servico.descricao = data.get('descricao', servico.descricao)
    servico.teste_bico = bool(data.get('teste_bico'))
    servico.teste_bomba = bool(data.get('teste_bomba'))
    servico.apenas_teste = bool(data.get('apenas_teste'))
    servico.mao_de_obra = float(data.get('mao_de_obra') or 0.0)
    
    # Deletar peças antigas
    Peca.query.filter_by(servico_id=servico_id).delete()
    
    # Adicionar novas peças
    total_pecas = 0.0
    for p in pecas:
        item = Peca(nome=p['nome'], unidade=p['unidade'], valor_unitario=p['valor_unitario'], servico_id=servico.id)
        db.session.add(item)
        total_pecas += item.valor_total
    
    # Atualizar nota
    nota = NotaServico.query.filter_by(servico_id=servico_id).first()
    if nota:
        nota.total_pecas = total_pecas
        nota.total = total_pecas + servico.mao_de_obra
    
    db.session.commit()
    return servico

def delete_service(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    
    # Deletar peças
    Peca.query.filter_by(servico_id=servico_id).delete()
    
    # Deletar nota
    NotaServico.query.filter_by(servico_id=servico_id).delete()
    
    # Deletar serviço
    db.session.delete(servico)
    db.session.commit()
    return True

def list_notas():
    return NotaServico.query.order_by(NotaServico.created_at.desc()).all()
