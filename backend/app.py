import os
from flask import Flask


try:
    from .connection import db, init_db
    from .views.main import main_bp
except Exception:
    from backend.connection import db, init_db
    from backend.views.main import main_bp


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    frontend_templates = os.path.join(base_dir, '..', 'frontend', 'templates')
    frontend_static = os.path.join(base_dir, '..', 'frontend', 'static')

    app = Flask(
        __name__,
        template_folder=frontend_templates,
        static_folder=frontend_static
    )
    

    # =========================
    # CONFIGURAÇÕES
    # =========================
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            'sqlite:///' +
            os.path.join(base_dir, '..', 'database', 'gr_diesel.db')
        )

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('GR_SECRET_KEY', 'dev-secret-key')

    # 🔴 ESSENCIAL PARA AS NOTAS PNG
    app.config['EXPORTS_PATH'] = os.path.join(
        base_dir, '..', 'frontend', 'static', 'exports'
    )

    # =========================
    # REGISTRAR BLUEPRINT
    # =========================
    from backend.routes import main_bp
    app.register_blueprint(main_bp)

    # =========================
    # INICIALIZAR DB
    # =========================
    with app.app_context():
        init_db(app)

    # =========================
    # CONTEXT PROCESSOR
    # =========================
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}

    # =========================
    # DEBUG ROUTES
    # =========================
    from flask import Response, jsonify

    @app.route('/debug/hello')
    def debug_hello():
        return 'ok'

    @app.route('/debug/routes')
    def debug_routes():
        rules = [str(r) for r in app.url_map.iter_rules()]
        return Response('\n'.join(sorted(rules)), mimetype='text/plain')

    @app.route('/debug/exports')
    def debug_exports():
        path = app.config['EXPORTS_PATH']
        try:
            files = sorted(os.listdir(path)) if os.path.exists(path) else []
        except Exception:
            files = []
        return jsonify(files=files)

    @app.route('/debug/servico/<int:servico_id>')
    def debug_servico(servico_id):
        """Retorna informações básicas do serviço para diagnóstico."""
        try:
            from backend.models import Servico
            servico = Servico.query.get(servico_id)
            if not servico:
                return Response('Serviço não encontrado', status=404, mimetype='text/plain')
            data = {
                'id': servico.id,
                'descricao': servico.descricao,
                'cliente_id': servico.cliente_id,
                'created_at': servico.created_at.isoformat() if getattr(servico, 'created_at', None) else None
            }
            return jsonify(data)
        except Exception as e:
            return Response(f'Erro ao ler serviço: {e}', status=500, mimetype='text/plain')

    @app.route('/debug/nota/<int:servico_id>/generate')
    def debug_nota_generate(servico_id):
        """Força a geração da nota para um serviço e retorna resultado rápido."""
        try:
            from backend.models import Servico
            servico = Servico.query.get(servico_id)
            if not servico:
                return Response('Serviço não encontrado', status=404, mimetype='text/plain')
            exports_path = app.config.get('EXPORTS_PATH')
            os.makedirs(exports_path, exist_ok=True)
            # use canonical filename so download endpoints can find it
            png_path = os.path.join(exports_path, f'nota_{servico.id}.png')
            try:
                from backend.services.print_service import generate_png_with_playwright
                generate_png_with_playwright(servico, png_path, app)
            except Exception as e:
                # tentar ler log se existir
                log_path = os.path.join(exports_path, f'print_error_{servico.id}.log')
                snippet = ''
                if os.path.exists(log_path):
                    with open(log_path, 'r', encoding='utf-8') as f:
                        snippet = f.read(1000)
                return Response(f'Erro gerando nota:\n{e}\n\nLog snippet:\n{snippet}', status=500, mimetype='text/plain')
            # check for either canonical or playwright variant
            can = os.path.join(exports_path, f'nota_{servico.id}.png')
            alt = os.path.join(exports_path, f'nota_{servico.id}_playwright.png')
            if os.path.exists(can) or os.path.exists(alt):
                return Response('Gerado com sucesso', mimetype='text/plain')
            return Response('Geração finalizada sem criar arquivo', status=500, mimetype='text/plain')
        except Exception as e:
            return Response(f'Erro inesperado: {e}', status=500, mimetype='text/plain')

    @app.route('/debug/nota/<int:servico_id>/log')
    def debug_nota_log(servico_id):
        exports_path = app.config.get('EXPORTS_PATH')
        log_path = os.path.join(exports_path, f'print_error_{servico_id}.log')
        if not os.path.exists(log_path):
            return Response('Log não encontrado', status=404, mimetype='text/plain')
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)
        except Exception:
            return Response('Erro ao ler o arquivo de log', status=500, mimetype='text/plain')
        return Response(content, mimetype='text/plain')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
