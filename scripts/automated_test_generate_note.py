"""Script rápido para criar cliente e registrar serviço via test client e verificar geração de nota PDF/PNG"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app import create_app
from backend.db import db
import os

app = create_app()
with app.test_client() as client:
    # create client
    resp = client.post('/cliente/novo', data={
        'nome': 'Cliente Teste',
        'telefone': '99999-0000',
        'endereco': 'Rua Teste, 123',
        'cidade': 'Brasilia',
        'cep': '70000-000',
        'estado': 'DF',
        'cnpj_cpf': '000.000.000-00',
        'inscricao_estadual': 'ISENTO',
        'modelo_veiculo': 'Modelo X',
        'placa': 'ABC-1234',
        'pessoa': 'PF',
        'forma_pagamento': 'Pix'
    }, follow_redirects=True)
    print('Cliente criado, status:', resp.status_code)

    # get client id
    # pegar cliente via DB direto (evita conflitos de import com pacote models)
    import sqlite3
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'gr_diesel.db'))
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM clientes WHERE nome = ?", ('Cliente Teste',))
    row = cur.fetchone()
    conn.close()
    if not row:
        print('Cliente não encontrado')
        raise SystemExit(1)
    cid = row[0]

    # register service with one item
    resp = client.post(f'/servico/novo/{cid}', data={
        'descricao': 'Serviço de teste',
        'data_emissao': '2025-12-22',
        'mao_de_obra': '150.00',
        'pecas_nome': ['Troca de peça A'],
        'pecas_qtde': ['1'],
        'pecas_valor': ['200.00']
    }, follow_redirects=True)
    print('Serviço criado, status:', resp.status_code)
    if resp.status_code >= 400:
        print('Resposta:', resp.data.decode('utf-8'))

    # verificar arquivo gerado
    with app.app_context():
        exports = app.config.get('EXPORTS_PATH')
        files = os.listdir(exports)
        print('Arquivos em exports:', files)
        # tentar encontrar nota_*.pdf
        notas = [f for f in files if f.startswith('nota_') and f.endswith('.pdf')]
        if notas:
            print('Nota(s) gerada(s):', notas)
        else:
            print('Nenhuma nota PDF encontrada')
