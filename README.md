# GR Diesel Eletro LTDA - Aplicação de controle de serviços

Estrutura básica criada para um site de oficina diesel com frontend, backend e banco de dados SQLite.

Como rodar (Windows / PowerShell):

1. Criar um virtualenv e instalar dependências:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate; pip install -r requirements.txt
```

2. Inicializar o banco (o arquivo sqlite será criado em database/gr_diesel.db):

```powershell
python database\init_db.py
```

3. Criar usuário patrão (opcional, para acessar a área de entradas):

```powershell
python SGU\create_owner_sgu.py
```

4. Rodar a aplicação (a partir da raiz do projeto):

```powershell
python main.py
```

Arquivos importantes:
- `SGU/` - pacote backend com `app`, `models`, `views`, `services` e `schemas`
- `frontend/` - templates e arquivos estáticos (CSS/JS)
- `database/` - scripts e arquivo sqlite (gerado)

Observações:
- A senha do patrão deve ser cadastrada manualmente no banco ou usando uma rota administrativa futura.

MySQL / Production notes
------------------------
Você pode executar a aplicação apontando para um banco MySQL definindo a variável de ambiente `DATABASE_URL`.

Exemplo (driver PyMySQL):

```powershell
$env:DATABASE_URL = "mysql+pymysql://usuario:senha@host:3306/nome_do_banco"
```

Se `DATABASE_URL` não estiver definida, a aplicação usará o SQLite local `database/gr_diesel.db` como fallback. Ao usar MySQL, instale o driver `pymysql` e certifique-se de que o banco exista (o SQLAlchemy criará as tabelas, não o banco em si).
