from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, current_app
from ..connection import db
from ..models.usuario import Cliente
from ..models.servico import Servico, Peca
from ..models.agendamento import NotaServico
from ..models.login import User
from ..services import client_service, servico_service, auth_service

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    servicos = servico_service.get_latest_services(limit=20)
    return render_template('index.html', servicos=servicos)


@main_bp.route('/clientes')
def clientes():
    clientes = client_service.list_clients()
    return render_template('clientes.html', clientes=clientes)


@main_bp.route('/cliente/novo', methods=['GET', 'POST'])
def cliente_novo():
    if request.method == 'POST':
        data = request.form.to_dict()
        client_service.create_client(data)
        flash('Cliente registrado com sucesso', 'success')
        return redirect(url_for('main.clientes'))
    return render_template('cliente_form.html')


@main_bp.route('/servico/novo', methods=['GET', 'POST'])
def servico_novo_noid():
    if request.method == 'POST':
        data = request.form.to_dict()
        cliente_choice = request.form.get('cliente_choice')
        if cliente_choice == 'none':
            cliente = client_service.get_or_create_anonymous_client()
            cliente_id = cliente.id
        elif cliente_choice and cliente_choice.startswith('existing_'):
            cliente_id = int(cliente_choice.split('_',1)[1])
        else:
            cliente_id = None

        pecas_n = request.form.getlist('pecas_nome')
        pecas_q = request.form.getlist('pecas_qtde')
        pecas_v = request.form.getlist('pecas_valor')
        pecas = []
        for n, q, v in zip(pecas_n, pecas_q, pecas_v):
            if not n:
                continue
            pecas.append({'nome': n, 'unidade': int(q or 1), 'valor_unitario': float(v or 0.0)})

        # se nenhum cliente_id, usar anônimo
        if not cliente_id:
            cliente = client_service.get_or_create_anonymous_client()
            cliente_id = cliente.id

        servico_service.create_service(cliente_id, data, pecas)
        flash('Serviço registrado com sucesso', 'success')
        return redirect(url_for('main.index'))

    # GET
    clientes = client_service.list_clients()
    return render_template('servico_form.html', cliente=None, clientes=clientes)


@main_bp.route('/servico/novo/<int:cliente_id>', methods=['GET', 'POST'])
def servico_novo(cliente_id):
    cliente = client_service.get_client(cliente_id)
    if request.method == 'POST':
        data = request.form.to_dict()
        pecas_n = request.form.getlist('pecas_nome')
        pecas_q = request.form.getlist('pecas_qtde')
        pecas_v = request.form.getlist('pecas_valor')
        pecas = []
        for n, q, v in zip(pecas_n, pecas_q, pecas_v):
            if not n:
                continue
            pecas.append({'nome': n, 'unidade': int(q or 1), 'valor_unitario': float(v or 0.0)})

        servico_service.create_service(cliente_id, data, pecas)
        flash('Serviço registrado com sucesso', 'success')
        return redirect(url_for('main.index'))

    return render_template('servico_form.html', cliente=cliente)


@main_bp.route('/nota/<int:servico_id>')
def nota(servico_id):
    servico = servico_service.get_service(servico_id)

    # tentar exibir o PNG gerado (se existir). Se não existir, renderiza o HTML da nota.
    from pathlib import Path
    exports_path = Path(current_app.config.get('EXPORTS_PATH') or Path(current_app.static_folder) / 'exports')
    png_name = f'nota_{servico.id}.png'
    alt_png_name = f'nota_{servico.id}_playwright.png'
    png_path = exports_path / png_name
    alt_png_path = exports_path / alt_png_name

    if png_path.exists() or alt_png_path.exists():
        png_use = png_name if png_path.exists() else alt_png_name
        png_url = url_for('static', filename=f'exports/{png_use}')
        return render_template('nota_view.html', servico=servico, png_url=png_url)

    return render_template('nota.html', servico=servico)


@main_bp.route('/servicos')
def servicos():
    servicos = servico_service.get_latest_services(limit=200)
    return render_template('servicos.html', servicos=servicos)


@main_bp.route('/servico/<int:servico_id>')
def servico_view(servico_id):
    servico = servico_service.get_service(servico_id)
    return render_template('servico_view.html', servico=servico)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if auth_service.login_user(username, password):
            flash('Login efetuado', 'success')
            return redirect(url_for('main.index'))
        flash('Usuário ou senha inválidos', 'danger')
    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    auth_service.logout()
    flash('Desconectado', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/entradas')
def entradas():
    if not session.get('is_owner'):
        flash('Acesso restrito', 'danger')
        return redirect(url_for('main.login'))
    notas = servico_service.list_notas()
    return render_template('entradas.html', notas=notas)


@main_bp.route('/export/clients')
def export_clients():
    exports_path = current_app.config.get('EXPORTS_PATH')
    if not exports_path:
        return "Export path not configured", 500
    file_path = exports_path.rstrip('/\\') + current_app.static_folder.replace(current_app.static_folder, '')
    # direct path to the file
    csv_path = f"{exports_path.rstrip('/\\')}\\clients_export.csv"
    try:
        return send_file(csv_path, as_attachment=True, download_name='clients_export.csv')
    except FileNotFoundError:
        flash('Arquivo de exportação não encontrado', 'warning')
        return redirect(url_for('main.clientes'))
