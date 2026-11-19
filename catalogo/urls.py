from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

# o path liga a URL com a view; como as views são classes, o .as_view() transforma em função
# <int:pk> pega o número da URL e passa pra view como pk (id do jogo)
# o name é usado no {% url %} dos templates e no reverse() das views
urlpatterns = [
    # páginas dos jogos
    path('', views.InicioView.as_view(), name='inicio'),
    path('jogos/', views.ListaJogosView.as_view(), name='lista_jogos'),
    path('jogos/novo/', views.NovoJogoView.as_view(), name='novo_jogo'),
    path('jogos/<int:pk>/', views.DetalheJogoView.as_view(), name='detalhe_jogo'),
    path('jogos/<int:pk>/editar/', views.EditarJogoView.as_view(), name='editar_jogo'),
    path('jogos/<int:pk>/excluir/', views.ExcluirJogoView.as_view(), name='excluir_jogo'),
    path('jogos/<int:pk>/avaliar/', views.AvaliarJogoView.as_view(), name='avaliar_jogo'),

    # contas (login e logout são views prontas do Django)
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    path('login/', auth_views.LoginView.as_view(template_name='catalogo/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
