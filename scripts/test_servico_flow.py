"""Testa criação de serviço com e sem cliente e verificação de geração de nota"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app import create_app
from backend.connection import db

app = create_app()

with app.test_client() as client:
    # garantir cliente de teste via SQL
    from sqlalchemy import text
    with app.app_context():
        # criar cliente de teste se não existir
        row = db.session.execute(text("SELECT id FROM clientes WHERE nome = :n"), {'n': 'Cliente Teste Flow'}).fetchone()
        if row:
            cid = row[0]
        else:
            db.session.execute(text("INSERT INTO clientes (nome, telefone, created_at) VALUES (:n,:t, datetime('now'))"), {'n':'Cliente Teste Flow','t':'0000'})
            db.session.commit()
            row = db.session.execute(text("SELECT id FROM clientes WHERE nome = :n"), {'n': 'Cliente Teste Flow'}).fetchone()
            cid = row[0]

    # GET form
    resp = client.get('/servico/novo')
    print('/servico/novo status', resp.status_code)
    assert resp.status_code == 200

    # POST service without client (cliente_choice=none)
    resp = client.post('/servico/novo', data={
        'cliente_choice': 'none',
        'descricao': 'Serv sem cliente',
        'data_emissao': '2025-12-22',
        'mao_de_obra': '50',
        'pecas_nome': ['Item A'],
        'pecas_qtde': ['1'],
        'pecas_valor': ['20']
    }, follow_redirects=True)
    print('POST sem cliente status', resp.status_code)
    assert resp.status_code == 200

    # verificar que última nota foi criada
    from sqlalchemy import text
    with app.app_context():
        row = db.session.execute(text('SELECT total FROM notas ORDER BY created_at DESC LIMIT 1')).fetchone()
        print('Última nota total:', row[0] if row else 'nenhuma')
        assert row is not None

    # POST service with existing client
    resp = client.post('/servico/novo', data={
        'cliente_choice': f'existing_{cid}',
        'descricao': 'Serv com cliente',
        'data_emissao': '2025-12-22',
        'mao_de_obra': '100',
        'pecas_nome': ['Item B'],
        'pecas_qtde': ['2'],
        'pecas_valor': ['30']
    }, follow_redirects=True)
    print('POST com cliente status', resp.status_code)
    assert resp.status_code == 200

    print('Teste de fluxo de serviço concluído com sucesso')