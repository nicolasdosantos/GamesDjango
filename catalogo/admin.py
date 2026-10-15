from django.contrib import admin

from .models import Avaliacao, Categoria, Desenvolvedora, Jogo, Plataforma


admin.site.register(Desenvolvedora)
admin.site.register(Categoria)
admin.site.register(Plataforma)


@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'desenvolvedora', 'plataforma', 'ano_lancamento', 'preco']


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['jogo', 'nome_usuario', 'nota', 'data']
