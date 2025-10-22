from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    # importa os modelos para que sejam registrados no MetaData
    from . import models  # noqa: F401
    db.create_all()
