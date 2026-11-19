# GameDex

Catálogo de jogos feito em Django para a atividade do curso de Análise e Desenvolvimento de Sistemas.

## Funcionalidades

- Lista de jogos com busca, filtros (categoria, plataforma, desenvolvedora, preço, ano e nota), ordenação e paginação
- Página de detalhe de cada jogo com as avaliações
- Cadastro de usuário, login e logout
- Avaliar jogos com nota de 1 a 5 e comentário
- Perfil do usuário com bio e plataforma favorita
- Cadastrar, editar e excluir jogos (só admin)
- Desenvolvedoras, categorias e plataformas são cadastradas pelo /admin/ do Django

## Níveis de acesso

- Visitante: só vê os jogos
- Usuário: avalia jogos e edita o próprio perfil
- Admin (is_staff): faz tudo do usuário e também cadastra, edita e exclui jogos

## Como rodar

O projeto usa MySQL (8.4 ou mais novo) ou MariaDB (10.11 ou mais novo). Primeiro crie o banco rodando o script com o usuário root:

```
mysql -u root -p < banco/gamedex.sql
```

O script já cria o banco `gamedex`, o usuário do projeto e os dados de exemplo.

```
python -m venv venv
source venv/bin/activate        (no Windows: venv\Scripts\activate)
pip install -r requirements.txt
python manage.py runserver
```

Depois é só abrir http://127.0.0.1:8000/

Logins de teste:

- Admin: `admin` / `admin123`
- Usuário: `usuario` / `usuario123`

Para usar SQLite sem instalar banco, troque o `DATABASES` no `gamedex/settings.py` (o bloco do SQLite já está lá comentado) e rode `python manage.py migrate`.

## Testes

```
python manage.py test
```
