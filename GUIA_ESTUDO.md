# Guia de estudo – GameDex

Catálogo de jogos feito em Django pra atividade da faculdade. O site lista jogos, mostra os detalhes de cada um, deixa cadastrar, editar e excluir jogos e receber avaliações (nota de 1 a 5 + comentário). Categorias e plataformas são cadastradas só pelo painel admin. Desenvolvedoras podem ser cadastradas no admin, mas também são criadas sozinhas quando alguém digita um nome novo no formulário de jogo.

- **Projeto:** `gamedex` (configurações gerais)
- **App:** `catalogo` (onde fica tudo do catálogo)
- **Banco:** MySQL (banco `gamedex`, criado pelo `banco/gamedex.sql`). O SQLite (`db.sqlite3`) continua no projeto como alternativa.
- **Front-end:** templates do Django + um arquivo CSS

Pra rodar: siga o `README.md` (instalar, rodar o script do banco, `python manage.py runserver`) e abra http://127.0.0.1:8000/

---

## 1. Como um pedido funciona (o caminho completo)

Exemplo: a pessoa abre **http://127.0.0.1:8000/jogos/5/**

```
Navegador pede /jogos/5/
      │
      ▼
gamedex/urls.py      → "admin/" não bate; '' manda pro include('catalogo.urls')
      │
      ▼
catalogo/urls.py     → 'jogos/<int:id>/' bate, id = 5 → chama views.detalhe_jogo(request, id=5)
      │
      ▼
catalogo/views.py    → get_object_or_404(Jogo, id=5) e jogo.avaliacoes.all()
      │                 (o ORM transforma isso em SQL e busca no MySQL)
      ▼
catalogo/models.py   → define como são as tabelas Jogo, Avaliacao etc.
      │
      ▼
render(...)          → junta detalhe_jogo.html (que estende base.html) com os dados
      │
      ▼
Navegador recebe o HTML pronto e carrega o style.css pelo /static/
```

Quando tem **formulário** (cadastrar, editar, avaliar), o caminho tem duas voltas:

1. **GET** – a pessoa abre a página → a view cria um form vazio (ou preenchido, na edição) → `render` mostra o formulário.
2. **POST** – a pessoa clica em Salvar → a view cria o form com `request.POST` → `is_valid()` confere tudo:
   - **válido:** `form.save()` grava no banco e depois `redirect` manda pra outra página;
   - **inválido:** `render` mostra o mesmo formulário com as mensagens de erro e o que já tinha sido digitado.

---

## 2. Arquivos do projeto

### `catalogo/models.py` – as tabelas do banco
Define os 5 models: **Desenvolvedora, Categoria, Plataforma, Jogo e Avaliacao**. Cada classe vira uma tabela e cada atributo vira uma coluna.

Relações:
- Desenvolvedora **1:N** Jogo (`ForeignKey`, `PROTECT`)
- Plataforma **1:N** Jogo (`ForeignKey`, `PROTECT`)
- Jogo **N:N** Categoria (`ManyToManyField`, o Django cria a tabela do meio sozinho)
- Jogo **1:N** Avaliacao (`ForeignKey`, `CASCADE`)

**Conexões:** as mudanças aqui viram arquivos em `migrations/` (makemigrations/migrate). O `admin.py` registra os models, o `forms.py` monta os ModelForms a partir deles, e as views buscam dados neles pelo ORM.

### `catalogo/admin.py` – o painel /admin/
Registra os 5 models no admin. `JogoAdmin` e `AvaliacaoAdmin` usam `list_display` pra mostrar mais colunas na lista. É o único lugar onde se cadastram categorias e plataformas, e o único onde dá pra preencher país e ano de fundação da desenvolvedora.

**Conexões:** usa os models e aparece em `/admin/` por causa do `gamedex/urls.py`.

### `catalogo/forms.py` – os formulários
- **JogoForm** (ModelForm de Jogo): a desenvolvedora é um campo de **texto**. No `save()`, ele procura a desenvolvedora pelo nome (sem ligar pra maiúsculas) e cria uma nova se não existir. As categorias aparecem como checkboxes.
- **AvaliacaoForm** (ModelForm de Avaliacao): só tem nome, nota e comentário. O jogo vem da URL e a data é automática.

**Conexões:** é baseado nos models e é usado pelas views `novo_jogo`, `editar_jogo` e `avaliar_jogo`. Aparece nos templates com `{{ form.as_div }}`.

### `catalogo/views.py` – a lógica das páginas
São 7 views em forma de função:

| View | URL | Template |
|---|---|---|
| `inicio` | `/` | `inicio.html` |
| `lista_jogos` | `/jogos/` | `lista_jogos.html` |
| `detalhe_jogo` | `/jogos/<id>/` | `detalhe_jogo.html` |
| `novo_jogo` | `/jogos/novo/` | `form_jogo.html` |
| `editar_jogo` | `/jogos/<id>/editar/` | `form_jogo.html` |
| `excluir_jogo` | `/jogos/<id>/excluir/` | `confirmar_exclusao.html` |
| `avaliar_jogo` | `/jogos/<id>/avaliar/` | `form_avaliacao.html` |

**Conexões:** são chamadas pelo `catalogo/urls.py`. Usam o model `Jogo` e os forms, e devolvem os templates acima com `render` (ou mandam pra outra URL com `redirect`).

### `catalogo/urls.py` – endereços do app
Liga cada URL a uma view e dá um `name` pra ela. Esse name é usado no `{% url %}` dos templates e no `redirect()` das views. O `<int:id>` pega o número da URL e passa pra view.

### `gamedex/urls.py` – endereços principais
É o primeiro urls.py que o Django lê (por causa do `ROOT_URLCONF`). Manda `admin/` pro painel e todo o resto pro `catalogo/urls.py` com `include`.

### `gamedex/settings.py` – configurações
As mais importantes: `INSTALLED_APPS` (o `catalogo` está lá), `DATABASES` (MySQL, com o SQLite comentado logo acima), `TEMPLATES` (`APP_DIRS=True` faz o Django achar `catalogo/templates/`), `STATIC_URL`, `LANGUAGE_CODE='pt-br'`, `TIME_ZONE`, `DEBUG` e `SECRET_KEY`. Também tem o `MIDDLEWARE`: as camadas que todo pedido atravessa antes da view. Uma delas, o `CsrfViewMiddleware`, é quem confere o `{% csrf_token %}`. Tem ainda `ALLOWED_HOSTS`, `BASE_DIR`, `USE_TZ` e `WSGI_APPLICATION`.

### Templates (`catalogo/templates/catalogo/`)
- **base.html** – o molde de todas as páginas: head, CSS, menu e rodapé. Tem os blocks `titulo` e `conteudo`. Marca no menu o link da página atual.
- **inicio.html** – a faixa de apresentação + os 3 últimos jogos.
- **lista_jogos.html** – todos os jogos em cards.
- **card_jogo.html** – pedaço reutilizável (via `include`) com o card de um jogo.
- **detalhe_jogo.html** – informações do jogo, categorias, botões e avaliações.
- **form_jogo.html** – formulário de cadastro **e** de edição de jogo.
- **form_avaliacao.html** – formulário de avaliação.
- **confirmar_exclusao.html** – a página "tem certeza?" antes de excluir.

Nos templates, `{{ }}` mostra um valor (com autoescape, que transforma `<` e `>` em texto pra ninguém injetar código) e `{% %}` faz lógica (if, for, url, block...). Comentários de template são `{# #}` e `{% comment %}`. Eles não aparecem no código-fonte da página, ao contrário do `<!-- -->` do HTML.

**Conexões:** todos menos o card e o base fazem `{% extends 'catalogo/base.html' %}`. Os links usam `{% url 'name' %}`, que vem do `catalogo/urls.py`. As variáveis (`jogo`, `jogos`, `form`...) vêm do dicionário que a view passa no `render`.

### `catalogo/static/catalogo/css/style.css` – o visual
Tema escuro roxo. Usa variáveis de cor (`--roxo`, `--fundo`...), flexbox e grid pros layouts e media queries pro celular. Algumas classes vêm do próprio Django, como `.errorlist` nos erros do formulário, e outras do template, como `nota-1` a `nota-5`.

**Conexões:** é carregado no `base.html` com `{% static %}`.

---

## 3. Arquivos de apoio do Django

São arquivos que o `startproject`/`startapp` criaram (ou que o Django gerou) e que eu quase não mexo, mas preciso saber pra que servem.

| Arquivo | Pra que serve |
|---|---|
| `manage.py` | Roda os comandos do Django: `runserver`, `makemigrations`, `migrate`, `createsuperuser`, `check`, `shell`, `test`. Ele só diz qual settings usar (`DJANGO_SETTINGS_MODULE = 'gamedex.settings'`) e repassa o comando. |
| `gamedex/wsgi.py` | Porta de entrada pra servidores WSGI (o padrão de como um servidor web conversa com Python). O `runserver` usa o `application` daqui, por causa do `WSGI_APPLICATION` no settings, e um servidor de produção (tipo gunicorn) também usaria. |
| `gamedex/asgi.py` | Mesma ideia, só que pra servidores ASGI (assíncronos, que aguentam websockets). **Não é usado** neste projeto. |
| `catalogo/apps.py` | Configuração do app (`CatalogoConfig`). O `'catalogo'` no `INSTALLED_APPS` aponta pra ela. |
| `catalogo/tests.py` | Lugar dos testes automáticos (`TestCase`, rodam com `manage.py test` num banco separado). **Está vazio**: o projeto não tem testes automáticos e foi testado na mão pelo navegador. |
| `__init__.py` (em `gamedex/`, `catalogo/` e `migrations/`) | Transformam a pasta num pacote Python, aí dá pra importar `gamedex.settings`, `catalogo.urls` etc. Sem o de `migrations/`, o Django acha que o app não tem migrations. Os de `catalogo/` e `migrations/` estão vazios. O de `gamedex/` tem o `pymysql.install_as_MySQLdb()`, porque ele roda antes de tudo (ver seção 5). |
| `requirements.txt` | Lista dos pacotes e versões que o projeto precisa: Django 6.1.2, PyMySQL (conexão com o MySQL) e `cryptography` (login no MySQL 8 com senha). `asgiref`, `sqlparse`, `cffi` e `pycparser` vêm junto como dependências. Num computador novo: criar a venv e rodar `pip install -r requirements.txt`. |
| `banco/gamedex.sql` | Script que cria o banco MySQL inteiro: banco, usuário, tabelas, migrations aplicadas e dados de exemplo (ver seção 5). |
| `README.md` | Passo a passo pra rodar o projeto em outro computador (Windows e Linux) e a seção "Deu erro?". |
| `venv/` | Ambiente virtual: uma pasta com um Python e os pacotes só deste projeto, pra não misturar com os de outros projetos. |
| `.gitignore` | Lista do que o Git não deve guardar: `venv/`, `__pycache__/`, `*.pyc` e configurações do editor. O `db.sqlite3` foi guardado de propósito, pra ir com os dados de exemplo. |
| `db.sqlite3` | O banco SQLite inteiro num arquivo só. Hoje o projeto usa MySQL, mas ele continua aqui (com os dados antigos) pra quem quiser voltar pro SQLite. |

### As migrations (`catalogo/migrations/`)

Uma migration é um arquivo com as instruções pra deixar o banco igual aos models. O ciclo é sempre este: mudo o `models.py` → `makemigrations` gera a migration → `migrate` aplica no banco. O Django anota numa tabela própria (`django_migrations`) o que já foi aplicado. Cada migration depende da anterior (`dependencies`), então elas formam uma fila.

| Migration | O que fez | Mudou o banco? |
|---|---|---|
| `0001_initial` | Criou as 5 tabelas e a tabela do meio do ManyToMany (`catalogo_jogo_categorias`). | Sim |
| `0002_alter_jogo_preco` | Adicionou o `MinValueValidator(0)` no preço. | **Não** (no-op): o validator só existe no Python, na validação do formulário |
| `0003_alter_desenvolvedora_…` | Deixou `pais` e `ano_fundacao` opcionais (`blank`/`null`). Era necessário pro JogoForm conseguir criar uma desenvolvedora só com o nome. | Sim |
| `0004_alter_…_options` | Adicionou `ordering = ['nome']` em Categoria e Plataforma. | **Não** (no-op): ordering é só a ordem padrão das buscas |

Dá pra conferir o SQL de cada uma com `python manage.py sqlmigrate catalogo 0002`. Nas no-op ele mostra só `-- (no-op)`.

---

## 4. Erros corrigidos

Na primeira rodada de comentários, 5 explicações estavam erradas ou imprecisas. Elas foram corrigidas nos arquivos. Ficam aqui porque são pontos fáceis de confundir.

**1. `max_length` do CharField** (`models.py`)
- **Dizia:** "O max_length é obrigatório e limita o tamanho no banco."
- **Certo:** nesta versão do Django com SQLite, o `max_length` **não é obrigatório** (em bancos como o MySQL é). E o **SQLite não confere tamanho de texto**: dá pra gravar 500 letras numa coluna de 100. Quem barra é a **validação do Django**: o formulário dá erro e o `<input>` ganha `maxlength`.

**2. Onde aparece o `__str__` da Desenvolvedora** (`models.py`)
- **Dizia:** "aparece no admin ou no select do formulário."
- **Certo:** no **site** a desenvolvedora é um **campo de texto** (o JogoForm troca o select por um `CharField`). O select de desenvolvedora só existe na tela de jogo do **admin**. O `__str__` aparece no admin, nesse select do admin e no `{{ jogo.desenvolvedora }}` dos templates.

**3. Quem cadastra desenvolvedoras** (`admin.py` e a introdução deste guia)
- **Dizia:** "Desenvolvedora, Categoria e Plataforma só são cadastradas por aqui [no admin]."
- **Certo:** só **Categoria e Plataforma** dependem do admin. A **Desenvolvedora também é criada pelo `JogoForm.save()`** quando a pessoa digita um nome que ainda não existe (`filter(nome__iexact=...).first()` e, se não achar, `create()`). Ela é criada só com o nome. País e ano ficam vazios e só podem ser preenchidos no admin.

**4. O que a `SECRET_KEY` assina** (`settings.py`)
- **Dizia:** "usa pra assinar os cookies de sessão e o token do csrf_token."
- **Certo:** o **csrf_token não usa a SECRET_KEY**. Ele é um código **aleatório** guardado num cookie, e quem confere é o `CsrfViewMiddleware`. A SECRET_KEY assina coisas como os **dados da sessão** (quem está logado no admin) e os **links de redefinir senha**.

**5. O que acontece sem o `TIME_ZONE`** (`settings.py`)
- **Dizia:** "Sem isso ficaria no horário UTC."
- **Certo:** **UTC é o valor que o `startproject` escreve** no settings. Se a linha fosse **apagada**, o Django usaria o padrão interno dele, que é **`America/Chicago`**. Por isso é bom deixar `America/Sao_Paulo` escrito. Ele também define o que é "hoje" pro `auto_now_add` da avaliação.

---

## 5. O banco de dados: SQLite e MySQL

### Qual a diferença?
| | SQLite | MySQL / MariaDB |
|---|---|---|
| Onde fica | Um arquivo (`db.sqlite3`) | Um servidor separado, que precisa estar instalado e ligado |
| Como o Django conecta | Abre o arquivo direto | Pela rede: host + porta + usuário + senha |
| Instalação | Nenhuma, já vem com o Python | Instalar o servidor + uma biblioteca de conexão (PyMySQL) |
| Usuários e permissões | Não tem | Tem (o projeto usa o usuário `gamedex`) |
| Pra que serve | Desenvolvimento, projetos pequenos | Sites de verdade, vários acessos ao mesmo tempo |

**O que mudou no código pra trocar de banco:** só o `DATABASES` do `settings.py`, o `requirements.txt` e duas linhas no `gamedex/__init__.py`. Models, views, forms e templates ficaram iguais, porque o ORM gera o SQL certo pra cada banco. Essa é a grande vantagem de usar o ORM em vez de escrever SQL na mão.

### PyMySQL
O Django conecta no MySQL usando uma biblioteca chamada `MySQLdb` (pacote `mysqlclient`). Esse pacote às vezes precisa de compilador pra instalar, principalmente no Windows. O PyMySQL é feito só em Python e instala sem problema. O `pymysql.install_as_MySQLdb()` no `gamedex/__init__.py` registra o PyMySQL com o nome `MySQLdb`, e o Django usa ele sem perceber a troca. O `cryptography` é necessário porque o MySQL 8 usa um tipo de login (`caching_sha2_password`) que precisa de criptografia quando o usuário tem senha.

### Usuário próprio do projeto
O script cria o usuário `gamedex` (senha `Gamedex@2026`) com permissão **só no banco gamedex** (`GRANT ALL PRIVILEGES ON gamedex.*`). Isso é o "princípio do menor privilégio": o projeto só pode mexer no que precisa. Se a senha vazar, os outros bancos do MySQL ficam protegidos. E como o usuário é igual em todo computador, o `settings.py` não precisa ser editado. O usuário é criado 3 vezes (`'localhost'`, `'127.0.0.1'` e `'::1'`) porque, dependendo da configuração, o MySQL identifica uma conexão local por um desses nomes.

### O que o `banco/gamedex.sql` faz
1. `DROP DATABASE IF EXISTS` + `CREATE DATABASE ... utf8mb4`: recria o banco do zero, por isso dá pra rodar o script várias vezes.
2. `CREATE USER IF NOT EXISTS` + `ALTER USER` + `GRANT`: cria o usuário (sem erro se já existir), garante a senha e dá a permissão.
3. `CREATE TABLE` das 16 tabelas: 10 internas do Django (auth, admin, contenttypes, sessions, django_migrations) e 6 do catálogo, incluindo a `catalogo_jogo_categorias` do ManyToMany.
4. `INSERT` na `django_migrations`, na `django_content_type` e na `auth_permission`.
5. `INSERT` dos dados de exemplo e do superusuário `admin` / `admin123`.

**Como ele foi feito:** em vez de escrever as tabelas na mão, rodei o `migrate` num MySQL 8.4 limpo, gravei os dados de exemplo pelo próprio Django e exportei com o `mysqldump`. Assim as tabelas são exatamente as que as migrations criam. Ele foi testado em MySQL 8.4, MariaDB 11.8 e MariaDB 10.11.

### A tabela `django_migrations`
É onde o Django anota quais migrations já foram aplicadas (colunas `app`, `name` e `applied`). O `migrate` **não olha as tabelas**: ele só compara a lista de arquivos de migration com essa tabela e roda o que estiver faltando. Como o script já insere as 22 linhas (as 18 migrations do Django e as 4 do catálogo), depois dele o `migrate` responde `No migrations to apply`. Se essa tabela estivesse vazia, o `migrate` tentaria criar tabelas que já existem e daria erro "Table already exists".

### Cuidado: o MySQL compara texto diferente do SQLite
A collation `utf8mb4_unicode_ci` ignora **maiúsculas e acentos** nas comparações. Então, no MySQL, uma categoria "Acao" é considerada igual a "Ação", e o `unique=True` do nome recusa a segunda. No SQLite isso passava. O mesmo vale pras buscas: um `filter(nome='rpg')` acha "RPG".

### Senha do admin
O `auth_user` não guarda a senha `admin123`. Ele guarda um **hash**: `pbkdf2_sha256$<iterações>$<salt>$<hash>`, gerado pelo `make_password` do Django. O hash não dá pra "desfazer". No login, o Django gera o hash do que foi digitado, com o mesmo salt, e compara os dois.

---

## 6. Perguntas que o professor pode fazer

**1. O que é o padrão MVT do Django?**
Model (dados/banco), View (lógica) e Template (HTML). No projeto: `models.py`, `views.py` e a pasta `templates/`. O `urls.py` liga a URL à view.

**2. O que é o ORM?**
É o que deixa eu mexer no banco com Python em vez de SQL. `Jogo.objects.all().order_by('titulo')` vira um `SELECT ... ORDER BY titulo`.

**3. O que é um QuerySet?**
É o resultado de uma busca do ORM, tipo uma lista de objetos. Ele só vai no banco quando eu uso de verdade (no for do template, por exemplo).

**4. Qual a diferença entre `get()`, `filter()` e `get_object_or_404()`?**
`get()` traz um objeto só e dá erro se não achar. `filter()` traz um QuerySet, que pode vir vazio. `get_object_or_404()` é um get que mostra 404 em vez de erro do servidor. Usei ele nas views de detalhe/editar/excluir/avaliar e o `filter().first()` no `JogoForm` pra procurar a desenvolvedora.

**5. Pra que servem `makemigrations` e `migrate`?**
`makemigrations` lê os models e gera um arquivo dizendo o que mudou. `migrate` aplica esse arquivo no banco (cria ou altera as tabelas).

**6. Por que PROTECT na desenvolvedora/plataforma e CASCADE na avaliação?**
Apagar uma desenvolvedora não pode apagar os jogos sem querer, então o PROTECT bloqueia. Avaliação sem jogo não faz sentido, então o CASCADE apaga junto.

**7. Como funciona a relação entre Jogo e Categoria?**
É N:N com `ManyToManyField`. O Django cria uma tabela intermediária com o id do jogo e o id da categoria. No template eu pego com `jogo.categorias.all`.

**8. Pra que serve o `related_name`?**
É o nome do caminho de volta da relação. Com `related_name='avaliacoes'` eu faço `jogo.avaliacoes.all()` pra pegar as avaliações de um jogo.

**9. Por que DecimalField no preço?**
O Decimal guarda o valor exato. O Float pode dar erro de arredondamento, o que é ruim com dinheiro.

**10. O que é um ModelForm e o que o `is_valid()` faz?**
ModelForm é um formulário gerado a partir de um model, então os campos e as validações já vêm de lá. O `is_valid()` confere os dados (obrigatórios, tipos, preço >= 0, nota entre as opções) e preenche o `cleaned_data`.

**11. Pra que serve o `save(commit=False)` no `avaliar_jogo`?**
Cria a avaliação sem salvar, porque ainda falta o jogo, que vem da URL e não do formulário. Coloco `avaliacao.jogo = jogo` e aí chamo `avaliacao.save()`.

**12. Qual a diferença entre GET e POST, e de onde vem o `request.POST`?**
GET é pra pegar uma página e POST é pra enviar dados que mudam alguma coisa. O `request.POST` tem o que a pessoa digitou no formulário. Por isso as views testam `if request.method == 'POST'`.

**13. Por que usar `redirect` depois de salvar, e não `render`?**
Pra evitar envio duplicado. Com render, o F5 reenvia o POST e cadastra de novo. Com redirect o navegador vai pra outra página com GET.

**14. O que é o `{% csrf_token %}`?**
É um campo escondido com um código secreto que o Django confere em todo POST. Isso protege contra outro site mandar um formulário falso usando o navegador da pessoa. Sem ele o Django dá erro 403.

**15. Por que a exclusão tem uma página de confirmação?**
Pra apagar só com POST. Se apagasse no GET, qualquer link ou clique errado apagaria o jogo.

**16. Como funciona a herança de templates?**
O `base.html` tem o layout e os `{% block %}`. As outras páginas fazem `{% extends 'catalogo/base.html' %}` e só preenchem os blocks. Assim o menu e o rodapé ficam num lugar só.

**17. Qual a diferença entre `extends` e `include`?**
`extends` é "esta página usa aquele molde". `include` é "coloque este pedaço aqui". O `card_jogo.html` é incluído na página inicial e na lista pra não repetir o HTML do card.

**18. Pra que servem o `name` das URLs e a tag `{% url %}`?**
Pra não escrever endereço na mão. `{% url 'detalhe_jogo' jogo.id %}` vira `/jogos/5/`. Se a URL mudar no `urls.py`, todos os links se ajustam.

**19. Como o Django acha os templates e o CSS?**
`APP_DIRS=True` faz ele procurar `templates/` dentro de cada app em `INSTALLED_APPS`. Os arquivos estáticos ficam em `static/` do app, e o `{% static %}` monta o endereço com o `STATIC_URL`.

**20. Por que as views não têm `@login_required`?**
O site não tem login de usuário, a pessoa só digita o nome na avaliação. O único lugar com login é o `/admin/`, que o Django já protege sozinho.

**21. Qual a diferença entre projeto e app?**
O projeto (`gamedex`) é o site inteiro: settings, URLs principais, wsgi. O app (`catalogo`) é uma parte com uma função, com models, views, templates e URLs próprios. Um projeto pode ter vários apps, e cada app precisa estar no `INSTALLED_APPS`.

**22. Qual a diferença entre `{{ }}` e `{% %}` no template?**
`{{ jogo.titulo }}` mostra um valor na página. `{% if %}`, `{% for %}`, `{% url %}` e os outros são tags que fazem lógica e não mostram nada sozinhas.

**23. O que é autoescape e por que ele importa?**
Tudo que sai por `{{ }}` tem os caracteres de HTML (`<`, `>`, `&`, aspas) trocados por códigos. Se alguém digitar `<script>` num comentário, aparece como texto e não roda. Isso protege contra XSS.

**24. Quem confere o csrf_token?**
O `CsrfViewMiddleware`, que está no `MIDDLEWARE` do settings. Ele roda antes da view em todo POST e devolve 403 se o token faltar ou estiver errado. O token é aleatório e não usa a SECRET_KEY.

**25. O que é middleware?**
São camadas que todo pedido atravessa antes de chegar na view (e a resposta na volta). Cada uma faz uma tarefa: sessão, autenticação, CSRF, segurança. A ordem da lista importa.

**26. Por que o projeto tem 4 migrations?**
Cada mudança no `models.py` gera uma nova. A 0001 criou as tabelas, a 0002 colocou o validator do preço, a 0003 deixou país e ano opcionais e a 0004 colocou o ordering. A 0002 e a 0004 nem mudam o banco (no-op), porque validator e ordering só existem no Python.

**27. De onde vem o `id` se eu não criei esse campo?**
O Django cria sozinho uma chave primária `id` (BigAutoField, um número que aumenta sozinho) em todo model. Dá pra ver na `0001_initial`. `pk` é outro nome pra ela.

**28. Pra que servem o `manage.py`, o `wsgi.py` e o `asgi.py`?**
`manage.py` roda os comandos (runserver, migrate...). `wsgi.py` é a porta de entrada do site pra um servidor web, e o próprio runserver usa ela. `asgi.py` é a versão assíncrona e não é usada aqui.

**29. Como você testou o projeto? Tem testes automáticos?**
O `tests.py` está vazio, então não tem testes automáticos. Testei na mão: cadastrando, editando, excluindo e avaliando jogos pelo site e conferindo no admin. Se fosse fazer testes, seriam classes `TestCase` rodadas com `python manage.py test`.

**30. Pra que servem a venv e o `requirements.txt`?**
A venv é um Python separado só pra este projeto, pra versão do Django não brigar com a de outros projetos. O `requirements.txt` lista os pacotes e versões, e com `pip install -r requirements.txt` qualquer pessoa instala tudo igual.

**31. O que você precisou mudar no código pra trocar o SQLite pelo MySQL?**
Só a configuração: o `DATABASES` no `settings.py`, o PyMySQL no `requirements.txt` e o `install_as_MySQLdb()` no `gamedex/__init__.py`. Models, views e templates não mudaram, porque o ORM gera o SQL de cada banco.

**32. Por que PyMySQL e não mysqlclient?**
O mysqlclient é o recomendado pelo Django, mas às vezes precisa de compilador pra instalar. O PyMySQL é só Python, instala em qualquer computador, e o `install_as_MySQLdb()` faz o Django usar ele no lugar.

**33. Por que o projeto tem um usuário próprio no MySQL em vez de usar o root?**
Pelo princípio do menor privilégio: o usuário `gamedex` só tem permissão no banco `gamedex`. Além disso, o root tem uma senha diferente em cada computador, e o `gamedex` é igual em todos, então o `settings.py` funciona sem editar.

**34. Depois de rodar o script, por que o `migrate` não tenta criar as tabelas de novo?**
Porque o script preenche a tabela `django_migrations` com todas as migrations. O `migrate` só olha essa tabela pra decidir o que rodar, então responde "No migrations to apply".

**35. Como esse script foi feito? Você escreveu as tabelas na mão?**
Não. Rodei o `migrate` num MySQL limpo, inseri os dados pelo Django e exportei com o `mysqldump`. Assim as tabelas são idênticas às que as migrations criam. Depois só organizei e comentei o arquivo.

**36. O que é utf8mb4 e o que é collation?**
utf8mb4 é o UTF-8 completo do MySQL (acentos, ç, emoji). A collation é a regra de comparar e ordenar texto. A `utf8mb4_unicode_ci` ignora maiúsculas e acentos, então "Ação" e "acao" contam como iguais.

**37. Como a senha do admin fica guardada no banco?**
Como hash `pbkdf2_sha256`, gerado pelo `make_password`. Não dá pra descobrir a senha olhando o banco. No login, o Django gera o hash da senha digitada e compara.

**38. Se eu mudar um model agora, o que acontece com o script?**
O fluxo normal continua: `makemigrations` e `migrate`, que funcionam com o usuário `gamedex` porque ele tem permissão de alterar tabelas no banco. Só que o `gamedex.sql` fica desatualizado e precisa ser gerado de novo pra quem for instalar o projeto do zero.
