import os
from flask import Flask

try:
    # quando usado como pacote (import backend.app)
    from .connection import db, init_db
    from .views.main import main_bp
except Exception:
    # quando executado como script (python backend/app.py)
    from backend.connection import db, init_db
    from backend.views.main import main_bp


def create_app():
    base_dir = os.path.dirname(__file__)
    frontend_templates = os.path.abspath(os.path.join(base_dir, '..', 'frontend', 'templates'))
    frontend_static = os.path.abspath(os.path.join(base_dir, '..', 'frontend', 'static'))

    app = Flask(__name__, template_folder=frontend_templates, static_folder=frontend_static)
    # Database configuration: allow override via DATABASE_URL env var (e.g. for MySQL)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'gr_diesel.db'))

    # Helpful engine option for remote DBs (MySQL) to keep connections healthy
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('GR_SECRET_KEY', 'dev-secret-key')
    # path where export files are written (frontend static exports)
    app.config['EXPORTS_PATH'] = os.path.abspath(os.path.join(base_dir, '..', 'frontend', 'static', 'exports'))

    # registrar blueprint
    app.register_blueprint(main_bp)

    # criar tabelas se estiver no contexto de app
    with app.app_context():
        init_db(app)

    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
