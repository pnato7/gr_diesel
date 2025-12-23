"""Script simples para adicionar colunas faltantes em SQLite (clientes).
Use: python database/migrate_add_client_fields.py
"""
import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'gr_diesel.db'))

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols

alter_statements = [
    ("clientes", "endereco", "TEXT"),
    ("clientes", "cidade", "TEXT"),
    ("clientes", "cep", "TEXT"),
    ("clientes", "estado", "TEXT"),
    ("clientes", "cnpj_cpf", "TEXT"),
    ("clientes", "inscricao_estadual", "TEXT"),
    ("servicos", "data_emissao", "DATETIME"),
]

if not os.path.exists(DB_PATH):
    print('Banco não encontrado em', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for table, column, coltype in alter_statements:
    if not column_exists(cur, table, column):
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {coltype};"
        print('Executando:', sql)
        cur.execute(sql)
    else:
        print(f'Coluna {column} já existe em {table}')

conn.commit()
conn.close()
print('Migração concluída')