import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Helpful import guidance if venv not activated
try:
    from backend.app import create_app
    from sqlalchemy import text
except ModuleNotFoundError as e:
    print('Erro de importação:', e)
    print('Sugestão: ative o venv do projeto e instale as dependências:')
    print('  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force')
    print('  & .\\.venv\\Scripts\\Activate.ps1')
    print('  pip install -r requirements.txt')
    sys.exit(1)

app = create_app()
# query DB inside app context before making test-client requests
with app.app_context():
    from backend.connection import db
    row = db.session.execute(text("SELECT id FROM servicos ORDER BY created_at DESC LIMIT 1")).fetchone()
    sid = row[0] if row else None

with app.test_client() as client:
    r = client.get('/servicos')
    print('/servicos ->', r.status_code)
    if sid:
        r2 = client.get(f'/servico/{sid}')
        print(f'/servico/{sid} ->', r2.status_code)
    else:
        print('No services in DB to test /servico/<id>')
