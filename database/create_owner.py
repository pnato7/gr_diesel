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
    username = 'patrao'
    password = 'trocar123'  # aconselhável alterar
    if User.query.filter_by(username=username).first():
        print('Usuário já existe')
    else:
        u = User(username=username, password=generate_password_hash(password), is_owner=True)
        db.session.add(u)
        db.session.commit()
        print('Usuário patrão criado: usuário=patrao senha=trocar123')
