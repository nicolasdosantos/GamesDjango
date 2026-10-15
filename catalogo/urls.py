from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('jogos/', views.lista_jogos, name='lista_jogos'),
    path('jogos/novo/', views.novo_jogo, name='novo_jogo'),
    path('jogos/<int:id>/', views.detalhe_jogo, name='detalhe_jogo'),
    path('jogos/<int:id>/editar/', views.editar_jogo, name='editar_jogo'),
    path('jogos/<int:id>/excluir/', views.excluir_jogo, name='excluir_jogo'),
    path('jogos/<int:id>/avaliar/', views.avaliar_jogo, name='avaliar_jogo'),
]
