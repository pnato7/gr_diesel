from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
    abort,
    current_app
)
from .db import db
from backend.models import Cliente, Servico, Peca, NotaServico, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file
import os


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    servicos = Servico.query.order_by(Servico.created_at.desc()).limit(20).all()
    return render_template('index.html', servicos=servicos)


@main_bp.route('/clientes')
def clientes():
    clientes = Cliente.query.order_by(Cliente.created_at.desc()).all()
    return render_template('clientes.html', clientes=clientes)


@main_bp.route('/cliente/novo', methods=['GET', 'POST'])
def cliente_novo():
    if request.method == 'POST':
        data = request.form
        cliente = Cliente(
            nome=data.get('nome'),
            telefone=data.get('telefone'),
            endereco=data.get('endereco'),
            cidade=data.get('cidade'),
            cep=data.get('cep'),
            estado=data.get('estado'),
            cnpj_cpf=data.get('cnpj_cpf'),
            inscricao_estadual=data.get('inscricao_estadual'),
            modelo_veiculo=data.get('modelo_veiculo'),
            placa=data.get('placa'),
            pessoa=data.get('pessoa'),
            forma_pagamento=data.get('forma_pagamento')
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente registrado com sucesso', 'success')
        return redirect(url_for('main.clientes'))
    return render_template('cliente_form.html')


@main_bp.route('/servico/novo', methods=['GET'])
def servico_novo_root_get():
    # renderizar formulário sem cliente selecionado
    clientes = Cliente.query.order_by(Cliente.nome).all()
    return render_template('servico_form.html', cliente=None, clientes=clientes)

@main_bp.route('/servico/novo', methods=['POST'])
def servico_novo_root_post():
    return servico_novo(None)

@main_bp.route('/servico/novo/<int:cliente_id>', methods=['GET', 'POST'])
def servico_novo(cliente_id):
    # permite criar serviço com cliente selecionado, sem cliente (placeholder) ou criando cliente antes
    cliente = None
    if cliente_id is not None:
        cliente = Cliente.query.get_or_404(cliente_id)

    # lista de clientes para seleção (quando não há cliente pré-selecionado)
    clientes = Cliente.query.order_by(Cliente.nome).all()

    if request.method == 'POST':
        data = request.form
        # decidir cliente: campo 'cliente_choice' pode ser 'none', 'existing_<id>' ou 'new'
        cliente_choice = data.get('cliente_choice')
        selected_cliente = None
        if cliente_choice:
            if cliente_choice == 'none':
                # usar cliente placeholder 'Cliente não registrado'
                selected_cliente = Cliente.query.filter_by(nome='Cliente não registrado').first()
                if not selected_cliente:
                    selected_cliente = Cliente(nome='Cliente não registrado')
                    db.session.add(selected_cliente)
                    db.session.commit()
            elif cliente_choice.startswith('existing_'):
                try:
                    cid = int(cliente_choice.split('_', 1)[1])
                    selected_cliente = Cliente.query.get(cid)
                except Exception:
                    selected_cliente = None
        # se a rota veio com cliente_id, usa ele a menos que cliente_choice sobreponha
        if cliente and not cliente_choice:
            selected_cliente = cliente

        # se nenhum cliente selecionado, manter como None e usar placeholder
        if not selected_cliente:
            selected_cliente = Cliente.query.filter_by(nome='Cliente não registrado').first()
            if not selected_cliente:
                selected_cliente = Cliente(nome='Cliente não registrado')
                db.session.add(selected_cliente)
                db.session.commit()

        # parse data_emissao as date if provided
        data_emissao = data.get('data_emissao')
        from datetime import datetime
        emissao_dt = None
        if data_emissao:
            try:
                emissao_dt = datetime.fromisoformat(data_emissao)
            except Exception:
                emissao_dt = None

        servico = Servico(
            cliente_id=selected_cliente.id,
            descricao=data.get('descricao'),
            data_emissao=emissao_dt,
            teste_bico=bool(data.get('teste_bico')),
            teste_bomba=bool(data.get('teste_bomba')),
            apenas_teste=bool(data.get('apenas_teste')),
            mao_de_obra=float(data.get('mao_de_obra') or 0.0)
        )
        db.session.add(servico)
        db.session.commit()

        # adicionar peças/itens
        nomes = request.form.getlist('pecas_nome')
        qts = request.form.getlist('pecas_qtde')
        valores = request.form.getlist('pecas_valor')
        total_pecas = 0.0
        for n, q, v in zip(nomes, qts, valores):
            if not n:
                continue
            p = Peca(nome=n, unidade=int(q or 1), valor_unitario=float(v or 0.0), servico_id=servico.id)
            db.session.add(p)
            total_pecas += p.valor_total

        nota = NotaServico(servico_id=servico.id, total_pecas=total_pecas, total=total_pecas + servico.mao_de_obra)
        db.session.add(nota)
        db.session.commit()

        # gerar PNG da nota via Playwright (forçar uso do Playwright)
        try:
            import os
            from flask import current_app
            exports_path = current_app.config.get('EXPORTS_PATH')
            os.makedirs(exports_path, exist_ok=True)
            png_path = os.path.join(exports_path, f'nota_{servico.id}.png')

            try:
                from backend.services.print_service import generate_png_with_playwright
                generate_png_with_playwright(servico, png_path, current_app)
                flash(f'Nota PNG gerada via Playwright: /static/exports/nota_{servico.id}.png', 'success')
            except Exception as e_pw:
                print('Erro ao gerar nota PNG via Playwright:', e_pw)
                flash('Serviço registrado, mas falha ao gerar nota PNG. Instale Playwright (pip install playwright) e execute "python -m playwright install chromium".', 'danger')
        except Exception as e:
            # não falhar a criação do serviço por conta da geração da imagem
            print('Erro ao preparar geração de nota PNG:', e)
            flash('Serviço registrado, mas falha ao gerar nota (ver logs).', 'warning')

        return redirect(url_for('main.index'))

    return render_template('servico_form.html', cliente=cliente, clientes=clientes)


@main_bp.route('/nota/<int:servico_id>')
def nota(servico_id):
    """Exibe a nota: se houver PNG gerado, exibe a imagem; caso contrário, renderiza a versão HTML."""
    servico = Servico.query.get_or_404(servico_id)
    exports_path = current_app.config.get('EXPORTS_PATH')
    png_name = f'nota_{servico.id}.png'
    alt_png_name = f'nota_{servico.id}_playwright.png'
    png_path = os.path.join(exports_path, png_name)
    alt_png_path = os.path.join(exports_path, alt_png_name)

    if os.path.exists(png_path) or os.path.exists(alt_png_path):
        png_use = png_name if os.path.exists(png_path) else alt_png_name
        png_url = url_for('static', filename=f'exports/{png_use}')
        return render_template('nota_view.html', servico=servico, png_url=png_url)

    # fallback para a versão HTML se não houver PNG
    return render_template('nota.html', servico=servico)


@main_bp.route('/nota/<int:servico_id>/download')
def nota_download(servico_id):
    # Serve o PNG como anexo; tenta gerar on-demand se não encontrar o arquivo.
    servico = Servico.query.get_or_404(servico_id)

    exports_path = current_app.config.get('EXPORTS_PATH')
    png_name = f'nota_{servico.id}.png'
    png_path = os.path.join(exports_path, png_name)
    alt_png_name = f'nota_{servico.id}_playwright.png'
    alt_png_path = os.path.join(exports_path, alt_png_name)

    # Se já existe qualquer variante, servir imediatamente
    try:
        if os.path.exists(png_path):
            # write debug file indicating success
            try:
                with open(os.path.join(exports_path, f'nota_{servico.id}_download_debug.log'), 'w', encoding='utf-8') as dbg:
                    dbg.write(f'Found canonical: {png_path}\n')
            except Exception:
                pass
            return send_file(png_path, mimetype='image/png', as_attachment=True, download_name=f'nota_servico_{servico.id}.png')
        if os.path.exists(alt_png_path):
            try:
                with open(os.path.join(exports_path, f'nota_{servico.id}_download_debug.log'), 'w', encoding='utf-8') as dbg:
                    dbg.write(f'Found alt (playwright): {alt_png_path}\n')
            except Exception:
                pass
            return send_file(alt_png_path, mimetype='image/png', as_attachment=True, download_name=f'nota_servico_{servico.id}.png')
    except Exception:
        # ignore and continue to attempt generation
        pass

    # Tentar gerar sob demanda
    try:
        os.makedirs(exports_path, exist_ok=True)
        from backend.services.print_service import generate_png_with_playwright
        try:
            # gerar para nome canônico
            generate_png_with_playwright(servico, png_path, current_app)
        except Exception as gen_exc:
            # se ocorreu erro, tentar read log e informar
            log_path = os.path.join(exports_path, f'print_error_{servico.id}.log')
            short_msg = None
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.read().splitlines()
                        snippet = '\n'.join(lines[:8])
                        short_msg = snippet
                except Exception:
                    short_msg = None
            if short_msg:
                flash('Falha ao gerar nota (ver log). Primeiro trecho:\n' + short_msg, 'danger')
            else:
                flash('Falha ao gerar nota. Verifique Playwright e se o browser foi instalado (python -m playwright install chromium).', 'danger')
            return redirect(url_for('main.nota', servico_id=servico.id))

        # esperar um pouco pelo arquivo
        import time
        waited = 0.0
        timeout = 5.0
        interval = 0.25
        while waited < timeout and not os.path.exists(png_path) and not os.path.exists(alt_png_path):
            time.sleep(interval)
            waited += interval

    except Exception as e:
        print('Erro ao preparar geração de nota on-demand:', e)
        flash('Erro inesperado ao tentar gerar a nota. Verifique logs do servidor.', 'danger')
        return redirect(url_for('main.nota', servico_id=servico.id))

    # Tentar servir qualquer arquivo que exista após a tentativa
    if os.path.exists(png_path):
        return send_file(png_path, mimetype='image/png', as_attachment=True, download_name=f'nota_servico_{servico.id}.png')
    if os.path.exists(alt_png_path):
        return send_file(alt_png_path, mimetype='image/png', as_attachment=True, download_name=f'nota_servico_{servico.id}.png')

    # write detailed debug info to exports to help diagnosis
    try:
        debug_path = os.path.join(exports_path, f'nota_{servico.id}_download_debug.log')
        with open(debug_path, 'w', encoding='utf-8') as dbg:
            dbg.write('Download attempt failed. Paths checked:\n')
            dbg.write(f'canonical: {png_path} -> {os.path.exists(png_path)}\n')
            dbg.write(f'alt: {alt_png_path} -> {os.path.exists(alt_png_path)}\n')
            dbg.write('Files in exports:\n')
            for f in sorted(os.listdir(exports_path)):
                dbg.write(' - ' + f + '\n')
    except Exception:
        pass

    flash('Arquivo de nota PNG não encontrado após tentativa de geração. Consulte o log em /static/exports/print_error_<id>.log', 'danger')
    return redirect(url_for('main.nota', servico_id=servico.id))


@main_bp.route('/nota/<int:servico_id>/generate', methods=['POST'])
def nota_generate(servico_id):
    """Gera (ou atualiza) a nota PNG para um serviço e redireciona de volta para a visualização."""
    servico = Servico.query.get_or_404(servico_id)
    exports_path = current_app.config.get('EXPORTS_PATH')
    os.makedirs(exports_path, exist_ok=True)
    png_path = os.path.join(exports_path, f'nota_{servico.id}.png')
    try:
        from backend.services.print_service import generate_png_with_playwright
        generate_png_with_playwright(servico, png_path, current_app)
        flash('Nota gerada com sucesso', 'success')
    except Exception as e:
        msg = str(e)
        # mensagem mais amigável caso Playwright não esteja instalado
        if 'Playwright is not installed' in msg or 'playwright' in msg.lower():
            flash('Falha ao gerar nota: Playwright não está instalado. Execute: pip install playwright && python -m playwright install chromium', 'danger')
        else:
            log_path = os.path.join(exports_path, f'print_error_{servico.id}.log')
            snippet = ''
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        snippet = f.read(1000)
                except Exception:
                    pass
            flash('Falha ao gerar nota. Verifique logs. ' + (snippet[:200] if snippet else msg), 'danger')
    return redirect(url_for('main.nota', servico_id=servico.id))

@main_bp.route('/debug/nota/<int:servico_id>/status')
def debug_nota_status(servico_id):
    """Retorna caminhos verificados e lista de arquivos em exports (diagnóstico)."""
    servico = Servico.query.get_or_404(servico_id)
    exports_path = current_app.config.get('EXPORTS_PATH')
    png_name = f'nota_{servico.id}.png'
    png_path = os.path.join(exports_path, png_name)
    alt_png_name = f'nota_{servico.id}_playwright.png'
    alt_png_path = os.path.join(exports_path, alt_png_name)
    data = {
        'exports_path': exports_path,
        'png_path': png_path,
        'png_exists': os.path.exists(png_path),
        'alt_png_path': alt_png_path,
        'alt_exists': os.path.exists(alt_png_path),
        'exports_files': sorted(os.listdir(exports_path)) if os.path.exists(exports_path) else []
    }
    from flask import jsonify
    return jsonify(data)

@main_bp.route('/nota/<int:servico_id>/png')
def nota_png(servico_id):
    """Retorna somente o PNG da nota; retorna 404 se não existir."""
    servico = Servico.query.get_or_404(servico_id)
    import os
    from flask import current_app, send_from_directory, abort
    exports_path = current_app.config.get('EXPORTS_PATH')
    png_name = f'nota_{servico.id}.png'
    png_path = os.path.join(exports_path, png_name)
    alt_png_name = f'nota_{servico.id}_playwright.png'
    alt_png_path = os.path.join(exports_path, alt_png_name)

    # servir qualquer variante existente
    if os.path.exists(png_path):
        return send_from_directory(exports_path, png_name, mimetype='image/png')
    if os.path.exists(alt_png_path):
        return send_from_directory(exports_path, alt_png_name, mimetype='image/png')

    # Tentativa on-demand semelhante ao endpoint de download
    try:
        os.makedirs(exports_path, exist_ok=True)
        from backend.services.print_service import generate_png_with_playwright
        try:
            generate_png_with_playwright(servico, png_path, current_app)
        except Exception:
            # se falhar, retornar 404 simples (o log será escrito em exports)
            abort(404)
        # esperar rápido pelo arquivo
        import time
        waited = 0.0
        timeout = 5.0
        interval = 0.25
        while waited < timeout and not os.path.exists(png_path) and not os.path.exists(alt_png_path):
            time.sleep(interval)
            waited += interval
        if os.path.exists(png_path):
            return send_from_directory(exports_path, png_name, mimetype='image/png')
        if os.path.exists(alt_png_path):
            return send_from_directory(exports_path, alt_png_name, mimetype='image/png')
    except Exception:
        pass
    abort(404)


@main_bp.route('/debug/exports')
def debug_exports():
    """Lista arquivos em exports para diagnóstico rápido."""
    import os
    from flask import current_app, jsonify
    exports_path = current_app.config.get('EXPORTS_PATH')
    files = []
    try:
        if os.path.exists(exports_path):
            files = sorted(os.listdir(exports_path))
    except Exception:
        files = []
    return jsonify(files=files)


@main_bp.route('/debug/routes')
def debug_routes():
    """Retorna as rotas registradas (lista leve de url_rules)."""
    from flask import current_app, Response
    try:
        rules = [str(r) for r in current_app.url_map.iter_rules()]
        return Response('\n'.join(sorted(rules)), mimetype='text/plain')
    except Exception as e:
        return Response(f'Erro ao listar rotas: {e}', status=500, mimetype='text/plain')


@main_bp.route('/debug/nota/<int:servico_id>/log')
def debug_nota_log(servico_id):
    """Retorna as primeiras linhas do log de geração para um serviço."""
    servico = Servico.query.get_or_404(servico_id)
    import os
    from flask import current_app, Response, abort
    exports_path = current_app.config.get('EXPORTS_PATH')
    log_path = os.path.join(exports_path, f'print_error_{servico.id}.log')
    if not os.path.exists(log_path):
        return Response('Log não encontrado', status=404, mimetype='text/plain')
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            # enviar as primeiras 2000 chars para evitar respostas enormes
            content = f.read(2000)
    except Exception:
        return Response('Erro ao ler o arquivo de log', status=500, mimetype='text/plain')
    return Response(content, mimetype='text/plain')


@main_bp.route('/servicos')
def servicos():
    servicos = Servico.query.order_by(Servico.created_at.desc()).all()
    return render_template('servicos.html', servicos=servicos)


@main_bp.route('/servico/<int:servico_id>')
def servico_view(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    return render_template('servico_view.html', servico=servico)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_owner'] = user.is_owner
            flash('Login efetuado', 'success')
            return redirect(url_for('main.index'))
        flash('Usuário ou senha inválidos', 'danger')
    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Desconectado', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/entradas')
def entradas():
    # rota protegida; apenas patrão (is_owner)
    if not session.get('is_owner'):
        flash('Acesso restrito', 'danger')
        return redirect(url_for('main.login'))
    notas = NotaServico.query.order_by(NotaServico.created_at.desc()).all()
    return render_template('entradas.html', notas=notas)
