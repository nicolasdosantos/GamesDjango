# GameDex

Catálogo de jogos feito em Django (projeto acadêmico).
Dá para ver os jogos, cadastrar, editar, excluir e deixar avaliações com nota de 1 a 5.
Desenvolvedoras, categorias e plataformas também podem ser gerenciadas pelo painel admin.

---

## 1. O que instalar antes

### Python (3.12 ou mais novo)
- **Windows:** baixe em https://www.python.org/downloads/ e, na primeira tela do instalador, **marque "Add python.exe to PATH"**.
- **Linux (Ubuntu/Debian):** `sudo apt install python3 python3-venv`

Para conferir, abra um terminal e digite:
```
python --version      (Windows)
python3 --version     (Linux)
```
Tem que aparecer `Python 3.12` ou maior.

### MySQL (8.4 ou mais novo) ou MariaDB (10.11 ou mais novo)
- **Windows:** baixe o **MySQL Server 8.4** em https://dev.mysql.com/downloads/mysql/ (opção "Windows (x86, 64-bit), MSI Installer"). Durante a instalação ele pede uma **senha para o usuário root**: anote, ela é usada no passo 5.
  Baixe também o **MySQL Workbench** em https://dev.mysql.com/downloads/workbench/ (é o programa com tela para rodar o script).
- **Linux (Ubuntu/Debian):** use o MariaDB, que já vem nos repositórios em uma versão compatível:
  ```
  sudo apt install mariadb-server
  sudo systemctl start mariadb
  ```

Para conferir:
- **Windows:** abra o MySQL Workbench e clique na conexão "Local instance". Se pedir a senha do root e conectar, está funcionando.
- **Linux:** `sudo mariadb -e "select version();"`: tem que mostrar `10.11` ou maior.

> ⚠️ Versões antigas não funcionam com o Django 6.1: o XAMPP costuma vir com MariaDB 10.4, e o pacote `mysql-server` do Ubuntu 24.04 é o MySQL 8.0. Veja a seção "Deu erro?".

---

## 2. Passo a passo

### Passo 1: Baixar o projeto
Baixe o projeto (no GitHub: botão **Code > Download ZIP**) e descompacte. Depois abra um terminal **dentro da pasta do projeto**, que é a pasta onde está o arquivo `manage.py`:

| Windows (Prompt de Comando) | Linux |
|---|---|
| `cd C:\caminho\da\pasta\do\projeto` | `cd ~/caminho/da/pasta/do/projeto` |

### Passo 2: Criar o ambiente virtual (venv)
O ambiente virtual é uma pasta com um Python só deste projeto.

| Windows | Linux |
|---|---|
| `python -m venv venv` | `python3 -m venv venv` |

### Passo 3: Ativar o ambiente virtual
| Windows (Prompt de Comando) | Windows (PowerShell) | Linux |
|---|---|---|
| `venv\Scripts\activate` | `venv\Scripts\Activate.ps1` | `source venv/bin/activate` |

Vai aparecer `(venv)` no começo da linha do terminal. **Esse passo precisa ser repetido toda vez que abrir um terminal novo.**

### Passo 4: Instalar as bibliotecas
Com o `(venv)` aparecendo, rode (igual no Windows e no Linux):
```
pip install -r requirements.txt
```

### Passo 5: Criar o banco de dados
O arquivo `banco/gamedex.sql` cria o banco, o usuário do projeto, as tabelas e os dados de exemplo. Ele precisa ser rodado **uma vez**, com o usuário **root**.

**Opção A: pelo MySQL Workbench (Windows)**
1. Abra o Workbench e entre na conexão "Local instance" com a senha do root.
2. Menu **File > Open SQL Script** e escolha o arquivo `banco/gamedex.sql` do projeto.
3. Clique no ícone do **raio** (Execute).
4. No final aparece `Banco gamedex criado com sucesso!`.

**Opção B: pelo terminal**

| Windows (Prompt de Comando) | Linux |
|---|---|
| `"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p`<br>digite a senha do root e depois:<br>`source C:/caminho/da/pasta/do/projeto/banco/gamedex.sql`<br>(no `source`, use barras `/`)<br>para sair: `exit` | `sudo mariadb < banco/gamedex.sql` |

Não precisa mexer no `settings.py`: o projeto já está configurado para o usuário que o script cria (`gamedex` / `Gamedex@2026`).

### Passo 6: Ligar o servidor
```
python manage.py runserver
```
Deixe esse terminal aberto. Para desligar, aperte `Ctrl + C`.

### Passo 7: Abrir no navegador
| O quê | Endereço |
|---|---|
| Site | http://127.0.0.1:8000/ |
| Painel admin | http://127.0.0.1:8000/admin/ |

Login do admin: usuário **admin**, senha **admin123**.

---

## 3. Deu erro?

**PowerShell: "a execução de scripts foi desabilitada neste sistema"** (ao ativar a venv)
Rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, responda `S` e tente ativar de novo. Ou use o **Prompt de Comando** (cmd) em vez do PowerShell, com `venv\Scripts\activate`.

**"python não é reconhecido como um comando"**
O Python foi instalado sem marcar "Add python.exe to PATH". Tente usar `py` no lugar de `python`, ou reinstale o Python marcando essa opção.

**"Did you install mysqlclient?" ou "No module named pymysql"**
As bibliotecas não foram instaladas na venv. Ative a venv (passo 3) e rode `pip install -r requirements.txt` de novo.

**"Can't connect to MySQL server on 'localhost'" (erro 2003)**
O MySQL não está ligado.
- Windows: abra **Serviços**, procure **MySQL84** e clique em **Iniciar**.
- Linux: `sudo systemctl start mariadb`

**"Access denied for user 'gamedex'" (erro 1045) ou "Unknown database 'gamedex'" (erro 1049)**
O script `banco/gamedex.sql` não foi rodado ou parou no meio. Rode de novo como root (passo 5). Pode rodar quantas vezes quiser: ele sempre recria tudo do zero.

**"Access denied for user 'root'" ao rodar o script**
- Windows: é a senha que você criou na instalação do MySQL.
- Linux: no MariaDB o root entra pelo `sudo`, sem senha: `sudo mariadb < banco/gamedex.sql`.

**Quero usar outro usuário do MySQL (ou mudei a senha do gamedex)**
Abra `gamedex/settings.py`, procure o bloco `DATABASES` do MySQL e troque o `USER` e o `PASSWORD`:
```python
'USER': 'seu_usuario',
'PASSWORD': 'sua_senha',
```
Esse usuário precisa ter permissão no banco `gamedex`. Com o root funciona, mas não é recomendado.

**"MySQL 8.4 or later is required" ou "MariaDB 10.11 or later is required"**
O MySQL/MariaDB instalado é antigo demais para o Django 6.1. Isso acontece com o XAMPP (MariaDB 10.4) e com o `mysql-server` do Ubuntu 24.04 (MySQL 8.0). Instale o MySQL 8.4 (Windows) ou o `mariadb-server` (Linux), como no item 1. Ou volte para o SQLite (seção 4).

**"That port is already in use" (porta 8000 ocupada)**
Rode em outra porta: `python manage.py runserver 8001` e abra http://127.0.0.1:8001/

**A porta 3306 está ocupada / tenho outro MySQL ou o XAMPP ligado**
Desligue o outro (no XAMPP, botão **Stop** do MySQL). Se o seu MySQL usa outra porta, troque o `'PORT': '3306'` no `settings.py`.

**Acentos estranhos (ex: "AÃ§Ã£o" no lugar de "Ação")**
Rode o script de novo pelo Workbench ou pelo comando do passo 5. Pelo terminal, também dá para forçar o UTF-8: `mysql -u root -p --default-character-set=utf8mb4`.
Se o erro aparece só **no terminal do MySQL** e o site está certo, não tem problema: é só o terminal do Windows mostrando os caracteres de outro jeito.

---

## 4. Voltar para o SQLite (sem MySQL)

O projeto ainda tem o arquivo `db.sqlite3`, com os dados antigos.
1. Abra `gamedex/settings.py` e procure `DATABASES`.
2. Tire o `#` do começo das 6 linhas do bloco **SQLite**.
3. Coloque `#` no começo de todas as linhas do bloco **MySQL** (de `DATABASES = {` até o `}` final dele).
4. Rode `python manage.py runserver` normalmente. Não precisa rodar nenhum script.

O usuário admin do SQLite é outro, com a senha que já existia nele. Se não lembrar a senha, rode `python manage.py changepassword admin`.
