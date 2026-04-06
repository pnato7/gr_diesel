# Re-export the single SQLAlchemy instance from connection.py to avoid
# creating multiple instances which break app registration.
from .connection import db as db, init_db as init_db_with_app


def init_db(app=None):
    """Initialize DB. Backwards-compatible:

    - If called with an app, delegate to connection.init_db(app) which calls
      db.init_app(app) and creates tables.
    - If called with no app (legacy), just import models and create tables
      assuming an active app context.
    """
    if app is not None:
        return init_db_with_app(app)
    # legacy path: import models and create tables in current app context
    from . import models  # noqa: F401
    db.create_all()
