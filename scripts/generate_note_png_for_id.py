"""Gera PNG da nota para um serviço existente sem criar/editar DB (útil para testar visual)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Helpful import errors when virtualenv isn't activated
try:
    from backend.app import create_app
    from flask import render_template
except ModuleNotFoundError as e:
    print('Erro de importação:', e)
    print('Sugestão: ative o venv do projeto e instale as dependências:')
    print('  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force  # PowerShell')
    print('  & .\.venv\Scripts\Activate.ps1')
    print('  pip install -r requirements.txt')
    sys.exit(1)

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
    png_path = os.path.join(exports_path, f'nota_{SERVICE_ID}_manual.png')
    from weasyprint import HTML, CSS
    base_url = app.static_folder
    CSS_PATH = os.path.join(base_url, 'css', 'site.css')
    print('Gerando', png_path)
    try:
        HTML(string=html, base_url=base_url).write_png(png_path, stylesheets=[CSS(CSS_PATH)])
        print('Gerado com sucesso:', png_path)
    except Exception as e:
        print('Falha ao gerar PNG com WeasyPrint:', e)
        print('Policy: geração somente em PNG. Nenhum PDF de fallback será criado.')
        sys.exit(1)
