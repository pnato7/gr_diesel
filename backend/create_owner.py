from .app import create_app
from .connection import db
from .models.login import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    username = 'patrao'
    password = 'trocar123'
    if User.query.filter_by(username=username).first():
        print('Usuário já existe')
    else:
        u = User(username=username, password=generate_password_hash(password), is_owner=True)
        db.session.add(u)
        db.session.commit()
        print('Usuário patrão criado: usuário=patrao senha=trocar123')
