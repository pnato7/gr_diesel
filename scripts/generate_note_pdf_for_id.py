"""Gera PDF da nota para um serviço existente sem criar/editar DB (útil para testar visual)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app import create_app
from flask import render_template

app = create_app()

SERVICE_ID = int(os.environ.get('SERVICE_ID', '6'))

with app.app_context():
    from backend.services.servico_service import get_service
    servico = get_service(SERVICE_ID)
    # render within a request context so url_for() and static files resolve
    with app.test_request_context('/'):
        html = render_template('nota.html', servico=servico)
    exports_path = app.config.get('EXPORTS_PATH')
    os.makedirs(exports_path, exist_ok=True)
    pdf_path = os.path.join(exports_path, f'nota_{SERVICE_ID}_manual.pdf')
    from weasyprint import HTML, CSS
    base_url = app.static_folder
    CSS_PATH = os.path.join(base_url, 'css', 'site.css')
    print('Gerando', pdf_path)
    HTML(string=html, base_url=base_url).write_pdf(pdf_path, stylesheets=[CSS(CSS_PATH)])
    print('Gerado com sucesso')
