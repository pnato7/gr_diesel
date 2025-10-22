"""Script para inicializar o banco SQLite (cria arquivo gr_diesel.db)"""
import os
from backend.app import create_app

app = create_app()

print('Banco inicializado em database/gr_diesel.db')
