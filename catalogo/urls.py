# path() liga um endereço (URL) a uma view.
from django.urls import path
# auth_views tem as views prontas do Django pra entrar (LoginView) e sair (LogoutView).
# Elas já são views baseadas em classe, eu só digo qual template usar.
from django.contrib.auth import views as auth_views

# Importo o arquivo views.py inteiro, aí uso views.InicioView, views.ListaJogosView...
from . import views

# urlpatterns é a lista que o Django lê pra saber qual view chamar.
# Ele compara o endereço acessado com cada path, de cima pra baixo, e usa o primeiro que bater.
# Essas URLs entram pelo include('catalogo.urls') do gamedex/urls.py, que está em '' (a raiz),
# então os endereços aqui ficam do jeito que estão escritos.
#
# Como as views são classes, cada uma é ligada com .as_view(). Ele transforma a classe numa função,
# que é o que o path() espera receber.
#
# O name='...' é um apelido da URL. Nos templates eu uso {% url 'lista_jogos' %} e nas views
# reverse('lista_jogos'), em vez de escrever "/jogos/" na mão. Se um dia eu mudar o endereço,
# só mudo aqui e todos os links continuam funcionando.
#
# <int:pk> é uma parte da URL que muda: o Django pega o número, confere se é inteiro
# (se não for dá 404) e passa pra view com o nome "pk". Antes era <int:id>, mas as views genéricas
# (DetailView, UpdateView, DeleteView) procuram o objeto por um parâmetro chamado "pk" (primary key).
urlpatterns = [
    # "/" -> página inicial
    path('', views.InicioView.as_view(), name='inicio'),
    # "/jogos/" -> lista de jogos com os filtros de pesquisa
    path('jogos/', views.ListaJogosView.as_view(), name='lista_jogos'),
    # "/jogos/novo/" -> formulário de cadastro (só admin)
    path('jogos/novo/', views.NovoJogoView.as_view(), name='novo_jogo'),
    # "/jogos/5/" -> detalhe do jogo de id 5
    path('jogos/<int:pk>/', views.DetalheJogoView.as_view(), name='detalhe_jogo'),
    # "/jogos/5/editar/" -> formulário de edição do jogo 5 (só admin)
    path('jogos/<int:pk>/editar/', views.EditarJogoView.as_view(), name='editar_jogo'),
    # "/jogos/5/excluir/" -> confirmação (GET) e exclusão (POST) do jogo 5 (só admin)
    path('jogos/<int:pk>/excluir/', views.ExcluirJogoView.as_view(), name='excluir_jogo'),
    # "/jogos/5/avaliar/" -> formulário de avaliação do jogo 5 (precisa estar logado)
    path('jogos/<int:pk>/avaliar/', views.AvaliarJogoView.as_view(), name='avaliar_jogo'),

    # Contas de usuário
    # "/cadastro/" -> criar conta de usuário comum
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    # "/login/" -> entrar. A LoginView já valida usuário e senha e cria a sessão.
    # Depois de entrar ela manda pro LOGIN_REDIRECT_URL do settings.py (ou pro ?next= da URL).
    path('login/', auth_views.LoginView.as_view(template_name='catalogo/login.html'), name='login'),
    # "/logout/" -> sair. A LogoutView só aceita POST (desde o Django 5), por isso o botão "Sair"
    # do menu é um formulário com csrf_token e não um link. Assim um link escondido em outro site
    # não consegue deslogar a pessoa. Depois de sair vai pro LOGOUT_REDIRECT_URL.
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # "/perfil/" -> meu perfil (precisa estar logado). Sem id na URL: é sempre o perfil de quem está logado.
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
