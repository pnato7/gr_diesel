from ..connection import db
from datetime import datetime


class NotaServico(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    total_pecas = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    servico = db.relationship('Servico', backref=db.backref('nota', uselist=False))
