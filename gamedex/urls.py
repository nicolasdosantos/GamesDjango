"""
URL configuration for gamedex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# include() serve pra "puxar" a lista de URLs de outro arquivo (no caso, o urls.py do app catalogo).
from django.urls import include, path

# Este é o urls.py PRINCIPAL do projeto. O settings.py aponta pra ele no ROOT_URLCONF,
# então é por aqui que todo pedido começa.
# Eu deixo aqui só as URLs gerais e mando o resto pro app. Assim cada app cuida das próprias URLs
# e este arquivo fica pequeno.
urlpatterns = [
    # "/admin/" -> painel de administração pronto do Django (os models aparecem lá por causa do admin.py)
    path('admin/', admin.site.urls),
    # '' (a raiz do site) -> manda pro catalogo/urls.py. O que sobrar do endereço
    # (ex: "jogos/5/") é procurado na lista de lá.
    path('', include('catalogo.urls')),
]
