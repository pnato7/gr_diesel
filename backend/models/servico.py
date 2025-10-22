from ..connection import db
from datetime import datetime


class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    descricao = db.Column(db.Text)
    teste_bico = db.Column(db.Boolean, default=False)
    teste_bomba = db.Column(db.Boolean, default=False)
    apenas_teste = db.Column(db.Boolean, default=False)
    mao_de_obra = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship('Cliente', backref=db.backref('servicos', lazy=True))


class Peca(db.Model):
    __tablename__ = 'pecas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    unidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Float, default=0.0)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'))

    servico = db.relationship('Servico', backref=db.backref('pecas', lazy=True))

    @property
    def valor_total(self):
        return (self.unidade or 0) * (self.valor_unitario or 0.0)
