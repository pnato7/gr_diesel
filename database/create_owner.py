import sys
import os

# garantir que a raiz do projeto está no sys.path quando executado diretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.connection import db
from backend.models.login import User
from werkzeug.security import generate_password_hash


app = create_app()

with app.app_context():
    # permite sobrescrever via variáveis de ambiente
    username = os.environ.get('OWNER_USERNAME', 'patrao')
    password = os.environ.get('OWNER_PASSWORD')

    # se não houver senha em env var, pedir interativamente (oculto)
    if not password:
        try:
            import getpass
            pw = getpass.getpass(f"Digite a senha para o usuário '{username}': ")
            if not pw:
                print('Senha vazia. Abortando.')
                raise SystemExit(1)
            pw_confirm = getpass.getpass('Confirme a senha: ')
            if pw != pw_confirm:
                print('Senhas não conferem. Abortando.')
                raise SystemExit(1)
            password = pw
        except Exception:
            print('Não foi possível solicitar a senha interativamente. Use a variável OWNER_PASSWORD.')
            raise SystemExit(1)

    existing = User.query.filter_by(username=username).first()
    if existing:
        print('Usuário já existe')
        # perguntar se deseja atualizar a senha
        try:
            resp = input(f"Atualizar senha do '{username}'? (s/N): ").strip().lower()
        except Exception:
            resp = 'n'
        if resp == 's':
            existing.password = generate_password_hash(password)
            db.session.commit()
            print('Senha atualizada com sucesso')
        else:
            print('Nenhuma alteração realizada')
    else:
        u = User(username=username, password=generate_password_hash(password), is_owner=True)
        db.session.add(u)
        db.session.commit()
        print(f"Usuário patrão criado: usuário={username}. A senha não será exibida por segurança.")
