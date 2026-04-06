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

        # Simple migration: add `data_emissao` column to `servicos` table if missing
        try:
            inspector = db.inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('servicos')]
            if 'data_emissao' not in cols:
                # SQLite supports ADD COLUMN for simple cases
                try:
                    db.session.execute("ALTER TABLE servicos ADD COLUMN data_emissao DATETIME")
                    db.session.commit()
                    print('Migration: added data_emissao column to servicos')
                except Exception:
                    # if ALTER TABLE fails, ignore but log
                    print('Migration: failed to add data_emissao column to servicos')
        except Exception:
            pass
