from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Inicializa o banco (cria tabelas).

    Nota: para projetos maiores recomendo usar Flask-Migrate/alembic. Esta função
    é intencionalmente simples: registra modelos e cria as tabelas quando o app
    está no contexto.
    """
    from . import models  # importa os modelos para registrar
    # registra a instância do SQLAlchemy no app
    db.init_app(app)
    with app.app_context():
        db.create_all()
