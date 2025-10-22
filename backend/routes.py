from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db import db
from .models import Cliente, Servico, Peca, NotaServico, User
from werkzeug.security import generate_password_hash, check_password_hash

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


@main_bp.route('/servico/novo/<int:cliente_id>', methods=['GET', 'POST'])
def servico_novo(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == 'POST':
        data = request.form
        servico = Servico(
            cliente_id=cliente.id,
            descricao=data.get('descricao'),
            teste_bico=bool(data.get('teste_bico')),
            teste_bomba=bool(data.get('teste_bomba')),
            apenas_teste=bool(data.get('apenas_teste')),
            mao_de_obra=float(data.get('mao_de_obra') or 0.0)
        )
        db.session.add(servico)
        db.session.commit()

        # adicionar peças simples (arrays não suportados via form sem JS complexo)
        # espera campos pecas_nome[], pecas_qtde[], pecas_valor[]
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

        flash('Serviço registrado com sucesso', 'success')
        return redirect(url_for('main.index'))

    return render_template('servico_form.html', cliente=cliente)


@main_bp.route('/nota/<int:servico_id>')
def nota(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    return render_template('nota.html', servico=servico)


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
