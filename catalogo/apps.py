# apps.py: configuração do app catalogo, criada pelo startapp.
# O 'catalogo' que está no INSTALLED_APPS do settings.py faz o Django achar esta classe
# (o name = 'catalogo' tem que bater com o nome da pasta do app).
# Daria pra colocar mais coisas aqui, tipo um nome bonito do app no admin, mas não precisei.

from django.apps import AppConfig


class CatalogoConfig(AppConfig):
    name = 'catalogo'
