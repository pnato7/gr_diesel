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

with app.app_context():
    from backend.connection import db
    row = db.session.execute(text("SELECT id FROM servicos ORDER BY created_at DESC LIMIT 1")).fetchone()
    sid = row[0] if row else None

with app.test_client() as client:
    if not sid:
        print('No services in DB to test /nota/<id>/png')
    else:
        r = client.get(f'/nota/{sid}/png')
        print(f'/nota/{sid}/png ->', r.status_code)
        if r.status_code == 200:
            exports_path = app.config.get('EXPORTS_PATH')
            os.makedirs(exports_path, exist_ok=True)
            out_path = os.path.join(exports_path, f'nota_{sid}_downloaded.png')
            with open(out_path, 'wb') as f:
                f.write(r.data)
            print('Arquivo salvo em', out_path, 'tamanho:', os.path.getsize(out_path))
        else:
            print('Resposta (texto):', r.get_data(as_text=True))
