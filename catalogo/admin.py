from django.contrib import admin

from .models import Avaliacao, Categoria, Desenvolvedora, Jogo, Perfil, Plataforma


# registra os models no painel /admin/
admin.site.register(Desenvolvedora)
admin.site.register(Categoria)
admin.site.register(Plataforma)


# list_display escolhe as colunas que aparecem na lista do admin
@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'desenvolvedora', 'plataforma', 'ano_lancamento', 'preco']


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['jogo', 'usuario', 'nota', 'data']


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'plataforma_favorita']
