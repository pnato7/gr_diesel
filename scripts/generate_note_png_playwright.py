"""Gera PNG da nota usando Playwright (não requer MSYS2)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Helpful import guidance
try:
    from backend.app import create_app
    from backend.services.servico_service import get_service
except ModuleNotFoundError as e:
    print('Erro de importação:', e)
    print('Sugestão: ative o venv e instale as dependências:')
    print('  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force')
    print('  & .\\.venv\\Scripts\\Activate.ps1')
    print('  pip install -r requirements.txt')
    sys.exit(1)

SERVICE_ID = int(os.environ.get('SERVICE_ID', '6'))

app = create_app()

with app.app_context():
    servico = get_service(SERVICE_ID)
    exports_path = app.config.get('EXPORTS_PATH')
    os.makedirs(exports_path, exist_ok=True)
    png_path = os.path.join(exports_path, f'nota_{SERVICE_ID}_playwright.png')
    try:
        from backend.services.print_service import generate_png_with_playwright
        generate_png_with_playwright(servico, png_path, app)
        print('Gerado com sucesso:', png_path)
    except Exception as e:
        print('Falha ao gerar PNG via Playwright:', e)
        print('Se Playwright não estiver instalado: pip install playwright')
        print('E instale o chromium: python -m playwright install chromium')
        sys.exit(1)
