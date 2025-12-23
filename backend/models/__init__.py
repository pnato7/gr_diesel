# Re-export models from their modules to avoid duplicate class definitions
# and ensure a single declarative registry is used.
from .usuario import Cliente  # defines clientes
from .servico import Servico, Peca  # servicos, pecas
from .agendamento import NotaServico  # notas
from .login import User  # users

__all__ = [
    'Cliente', 'Servico', 'Peca', 'NotaServico', 'User'
]
