# path() liga um endereço (URL) a uma view.
from django.urls import path

# Importo o arquivo views.py inteiro, aí uso views.inicio, views.lista_jogos...
from . import views

# urlpatterns é a lista que o Django lê pra saber qual view chamar.
# Ele compara o endereço acessado com cada path, de cima pra baixo, e usa o primeiro que bater.
# Essas URLs entram pelo include('catalogo.urls') do gamedex/urls.py, que está em '' (a raiz),
# então os endereços aqui ficam do jeito que estão escritos.
#
# O name='...' é um apelido da URL. Nos templates eu uso {% url 'lista_jogos' %} e nas views
# redirect('lista_jogos'), em vez de escrever "/jogos/" na mão. Se um dia eu mudar o endereço,
# só mudo aqui e todos os links continuam funcionando.
#
# <int:id> é uma parte da URL que muda: o Django pega o número, confere se é inteiro
# (se não for dá 404) e passa pra view como o parâmetro "id".
urlpatterns = [
    # "/" -> página inicial (view inicio)
    path('', views.inicio, name='inicio'),
    # "/jogos/" -> lista de todos os jogos
    path('jogos/', views.lista_jogos, name='lista_jogos'),
    # "/jogos/novo/" -> formulário de cadastro.
    # Fica antes do <int:id>/ mas nem precisaria: "novo" não é número, então não ia bater lá de qualquer jeito.
    path('jogos/novo/', views.novo_jogo, name='novo_jogo'),
    # "/jogos/5/" -> detalhe do jogo de id 5
    path('jogos/<int:id>/', views.detalhe_jogo, name='detalhe_jogo'),
    # "/jogos/5/editar/" -> formulário de edição do jogo 5
    path('jogos/<int:id>/editar/', views.editar_jogo, name='editar_jogo'),
    # "/jogos/5/excluir/" -> confirmação (GET) e exclusão (POST) do jogo 5
    path('jogos/<int:id>/excluir/', views.excluir_jogo, name='excluir_jogo'),
    # "/jogos/5/avaliar/" -> formulário de avaliação do jogo 5
    path('jogos/<int:id>/avaliar/', views.avaliar_jogo, name='avaliar_jogo'),
]
