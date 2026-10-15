# O admin é o painel pronto que o Django dá em /admin/. Com ele dá pra cadastrar, editar e apagar
# dados sem eu precisar criar telas. Só entra quem tem usuário de staff (criei com createsuperuser).
from django.contrib import admin

from .models import Avaliacao, Categoria, Desenvolvedora, Jogo, Plataforma


# register() faz o model aparecer no painel do admin com a tela padrão.
# Eu decidi não fazer telas no site pra Desenvolvedora, Categoria e Plataforma.
# O site só tem CRUD de Jogo e o formulário de avaliação.
# Categoria e Plataforma só são cadastradas por aqui. A Desenvolvedora também pode ser criada
# sem passar pelo admin: quando alguém digita um nome novo no formulário de jogo, o JogoForm cria
# ela sozinho (ver forms.py). Mas o país e o ano de fundação só dá pra preencher aqui no admin.
admin.site.register(Desenvolvedora)
admin.site.register(Categoria)
admin.site.register(Plataforma)


# @admin.register(Jogo) é um decorator: uma linha com @ em cima da classe que "embrulha" ela.
# Aqui ele faz a mesma coisa que admin.site.register(Jogo, JogoAdmin), só que escrito em cima da classe.
# JogoAdmin: configura como os jogos aparecem no admin. O Django usa ela quando eu abro a lista de jogos lá.
# Não retorna nada, é só configuração.
@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    # list_display escolhe as colunas da tabela na lista do admin.
    # Sem isso aparecia só o __str__ (o título), e eu não via desenvolvedora, preço, etc.
    list_display = ['titulo', 'desenvolvedora', 'plataforma', 'ano_lancamento', 'preco']


# AvaliacaoAdmin: mesma ideia, mostra as colunas mais úteis da avaliação na lista do admin.
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['jogo', 'nome_usuario', 'nota', 'data']
