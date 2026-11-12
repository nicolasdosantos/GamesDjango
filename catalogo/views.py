# login: função do Django que "loga" o usuário (cria a sessão dele), usei no cadastro.
from django.contrib.auth import login
# UserCreationForm: formulário pronto do Django pra criar usuário (username, senha e confirmação da senha).
# Ele já valida tudo: username repetido, senha fraca, as duas senhas diferentes...
from django.contrib.auth.forms import UserCreationForm
# Mixins de permissão. Mixin é uma classe que eu "somo" na minha view pra ganhar um comportamento pronto:
# - LoginRequiredMixin: só deixa entrar quem está logado. Quem não está vai pra página de login.
# - UserPassesTestMixin: só deixa entrar quem passar no teste do método test_func().
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# get_object_or_404: busca um objeto no banco e, se não achar, mostra erro 404 (página não encontrada)
from django.shortcuts import get_object_or_404, redirect
# reverse monta o endereço a partir do name da URL (igual o {% url %} dos templates).
# reverse_lazy é a mesma coisa, só que "preguiçoso": só monta o endereço quando for usar.
# Uso ele nos atributos da classe (success_url), porque eles são lidos quando o Python carrega
# o arquivo, e nessa hora as URLs ainda não foram carregadas. O reverse normal ia dar erro ali.
from django.urls import reverse, reverse_lazy
# As views genéricas do Django. Cada uma já faz um tipo de página comum:
# - TemplateView: só mostra um template
# - ListView: mostra uma lista de objetos
# - DetailView: mostra um objeto só
# - CreateView / UpdateView / DeleteView: cadastrar, editar e excluir com formulário
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import AvaliacaoForm, FiltroJogoForm, JogoForm, PerfilForm
from .models import Avaliacao, Jogo, Perfil


# View = o código que recebe um pedido do navegador (o "request") e devolve uma resposta (uma página).
# O urls.py é quem decide qual view roda pra cada endereço.
#
# Antes as views eram funções (FBV, function-based views). A atividade pede views baseadas em classe
# (CBV, class-based views), então troquei todas. A diferença:
# - Na função eu escrevia tudo na mão: if request.method == 'POST', form.is_valid(), form.save(), render...
# - Na classe eu herdo de uma view genérica do Django que já faz esse caminho todo. Eu só digo
#   o model, o form e o template, e sobrescrevo (escrevo de novo) só os métodos que precisam ser diferentes.
# No urls.py a classe é ligada com .as_view(), que transforma a classe numa função que o Django sabe chamar.
#
# Níveis de usuário do site:
# - visitante (não logado): só vê os jogos
# - user (usuário comum, cadastrado pelo site): vê os jogos, avalia e edita o próprio perfil
# - admin (usuário com is_staff=True): faz tudo do user e ainda cadastra, edita e exclui jogos.
#   O is_staff é o mesmo campo que libera a entrada no /admin/ do Django.


# AdminRequiredMixin: mixin que eu criei pra liberar uma página só pro admin.
# Uso ele nas views de cadastrar, editar e excluir jogo.
# Ele herda do UserPassesTestMixin, que roda o test_func() antes da view:
# - se retornar True, a página abre normalmente
# - se retornar False e a pessoa NÃO está logada, ela vai pra página de login
# - se retornar False e a pessoa está logada (é um user comum), aparece erro 403 (acesso proibido)
# Essa checagem é o que protege de verdade. Esconder o botão no template não basta, porque a pessoa
# poderia digitar /jogos/1/excluir/ direto na barra de endereço.
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # request.user é o usuário logado (ou um "AnonymousUser" quando ninguém está logado,
        # que sempre tem is_staff=False). Então visitante e user comum não passam.
        return self.request.user.is_staff


# InicioView: página inicial do site.
# Roda quando a pessoa acessa "/" (a raiz do site).
# TemplateView só mostra um template. Eu sobrescrevi o get_context_data pra mandar os jogos em destaque.
class InicioView(TemplateView):
    template_name = 'catalogo/inicio.html'

    # get_context_data monta o "contexto": as variáveis que o template vai poder usar.
    # O **kwargs recebe o que vier da URL, e o super() traz o contexto que o Django já monta sozinho.
    # Eu só acrescento a minha variável e devolvo o dicionário.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Jogo.objects é o "gerenciador" do model, é por ele que o ORM faz as buscas no banco.
        # ORM = o Django traduz esse código Python pra SQL, então eu não escrevo SQL na mão.
        # order_by('-id'): o "-" é ordem decrescente, então o id maior (cadastrado por último) vem primeiro.
        # [:3] limita a 3 resultados. O Django transforma isso em LIMIT 3 no SQL e não traz todos os jogos.
        context['destaques'] = Jogo.objects.all().order_by('-id')[:3]
        return context


# ListaJogosView: mostra os jogos do catálogo, com os filtros de pesquisa.
# Roda quando acessa "/jogos/". Com filtro a URL fica tipo "/jogos/?titulo=zelda&plataforma=2".
# A ListView busca a lista no get_queryset() e manda pro template com o nome do context_object_name.
class ListaJogosView(ListView):
    model = Jogo
    template_name = 'catalogo/lista_jogos.html'
    # Sem isso a lista ia se chamar "object_list" (ou "jogo_list") no template. Com "jogos" fica mais claro.
    context_object_name = 'jogos'

    # get_queryset: decide QUAIS jogos aparecem. É aqui que os filtros entram.
    def get_queryset(self):
        # Começo com todos os jogos em ordem alfabética e vou "afunilando" com cada filtro preenchido.
        # O QuerySet só vai pro banco quando é usado de verdade, então cada .filter() aqui
        # só acrescenta uma condição no WHERE do SQL, sem fazer uma busca nova por filtro.
        jogos = Jogo.objects.all().order_by('titulo')

        # Os filtros chegam pelo request.GET (os parâmetros depois do "?" na URL).
        # Uso GET e não POST porque buscar não muda nada no banco, e assim o link com o filtro
        # pode ser salvo ou compartilhado. Passo pro FiltroJogoForm pra ele conferir os valores.
        self.form_filtro = FiltroJogoForm(self.request.GET)

        # Se algum valor for inválido (ex: ?preco_max=abc), o is_valid() dá False e eu mostro
        # a lista sem filtro, com a mensagem de erro do lado do campo.
        if self.form_filtro.is_valid():
            # cleaned_data: os valores já conferidos. Nos ModelChoiceField ele já vem como objeto
            # (uma Categoria, uma Plataforma...) e não como o id em texto.
            dados = self.form_filtro.cleaned_data

            # Cada if só aplica o filtro se o campo foi preenchido (campo vazio vem como '' ou None).
            if dados['titulo']:
                # titulo__icontains = "o título contém esse texto", sem ligar pra maiúscula/minúscula.
                # Vira um LIKE '%zelda%' no SQL. Então "zel" já acha "The Legend of Zelda".
                # O ORM manda o texto separado do SQL, então não tem como fazer SQL injection pela busca.
                jogos = jogos.filter(titulo__icontains=dados['titulo'])
            if dados['categoria']:
                # categorias é ManyToMany. O filter por ele traz os jogos que têm essa categoria
                # (o Django faz o JOIN com a tabela do meio sozinho).
                jogos = jogos.filter(categorias=dados['categoria'])
            if dados['plataforma']:
                jogos = jogos.filter(plataforma=dados['plataforma'])
            if dados['desenvolvedora']:
                jogos = jogos.filter(desenvolvedora=dados['desenvolvedora'])
            # Aqui eu comparo com "is not None" e não só "if", porque preço 0 é um filtro válido
            # (mostrar só os gratuitos), e 0 contaria como falso num if normal.
            if dados['preco_max'] is not None:
                # preco__lte = "preço menor ou igual a" (lte = less than or equal).
                jogos = jogos.filter(preco__lte=dados['preco_max'])

        return jogos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mando o formulário de filtro pro template desenhar os campos.
        # Como ele foi criado com o request.GET, os campos já aparecem com o que a pessoa buscou.
        context['form_filtro'] = self.form_filtro
        return context


# DetalheJogoView: mostra a página de um jogo específico com as avaliações dele.
# Roda quando acessa "/jogos/<pk>/", tipo "/jogos/5/".
# A DetailView pega o <int:pk> da URL e busca o jogo sozinha. Se não existir, ela já dá 404
# (é o mesmo que eu fazia antes com o get_object_or_404).
class DetalheJogoView(DetailView):
    model = Jogo
    template_name = 'catalogo/detalhe_jogo.html'
    context_object_name = 'jogo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object é o jogo que a DetailView buscou.
        # jogo.avaliacoes funciona por causa do related_name='avaliacoes' no ForeignKey do model Avaliacao.
        # select_related('usuario') já traz o usuário de cada avaliação no mesmo SQL (com JOIN).
        # Sem ele, o template ia fazer uma consulta nova no banco pra cada avaliação, só pra mostrar o nome.
        context['avaliacoes'] = self.object.avaliacoes.select_related('usuario').order_by('-data')
        return context


# NovoJogoView: cadastra um jogo novo. Só o admin entra (AdminRequiredMixin).
# Roda quando acessa "/jogos/novo/".
# A CreateView faz sozinha o que eu fazia na função: no GET mostra o formulário vazio, no POST
# roda o is_valid(), e se der certo chama o form.save() e redireciona. Se der errado, mostra os erros.
# O AdminRequiredMixin vem ANTES da CreateView na lista, porque o Python procura os métodos
# da esquerda pra direita. Assim a checagem de permissão roda antes da página.
class NovoJogoView(AdminRequiredMixin, CreateView):
    model = Jogo
    form_class = JogoForm
    template_name = 'catalogo/form_jogo.html'
    # extra_context = variáveis fixas que vão pro template. O form_jogo.html é usado
    # pra cadastrar e pra editar, e o que muda é o título da página.
    extra_context = {'titulo_pagina': 'Cadastrar jogo'}

    # get_success_url: pra onde ir depois de salvar. Vou pra página do jogo novo.
    # Uso redirect (é o que a CreateView faz) e não render, assim o F5 não cadastra o jogo duas vezes.
    # self.object é o jogo que acabou de ser salvo. Preciso do pk dele pra montar o endereço.
    def get_success_url(self):
        return reverse('detalhe_jogo', args=[self.object.pk])


# EditarJogoView: altera um jogo que já existe. Só o admin entra.
# Roda quando acessa "/jogos/<pk>/editar/".
# A UpdateView busca o jogo pelo pk da URL e abre o formulário já preenchido (é o instance=jogo de antes).
class EditarJogoView(AdminRequiredMixin, UpdateView):
    model = Jogo
    form_class = JogoForm
    template_name = 'catalogo/form_jogo.html'

    # get_object: busca o jogo que vai ser editado. Sobrescrevi só pra guardar o título original.
    # O is_valid() copia pro jogo, na memória, os campos que passaram na validação, mesmo quando
    # outro campo deu erro (ele só não salva no banco). Se a pessoa mudasse o título e errasse o preço,
    # a página ia mostrar "Editar jogo: <título que nem foi salvo>". Guardando antes, isso não acontece.
    def get_object(self, queryset=None):
        jogo = super().get_object(queryset)
        self.titulo_original = jogo.titulo
        return jogo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar jogo: {self.titulo_original}'
        return context

    def get_success_url(self):
        return reverse('detalhe_jogo', args=[self.object.pk])


# ExcluirJogoView: apaga um jogo. Só o admin entra.
# Roda quando acessa "/jogos/<pk>/excluir/".
# - GET: mostra a página "tem certeza?"
# - POST: apaga de verdade e volta pra lista de jogos
# A DeleteView só apaga no POST, nunca no GET. Se apagasse no GET, bastava abrir o link pra perder o jogo.
class ExcluirJogoView(AdminRequiredMixin, DeleteView):
    model = Jogo
    template_name = 'catalogo/confirmar_exclusao.html'
    context_object_name = 'jogo'
    # Depois de apagar o jogo não existe mais, então volto pra lista.
    # Aqui é reverse_lazy porque é um atributo da classe (ver explicação lá no import).
    # As avaliações do jogo vão junto por causa do on_delete=CASCADE no model Avaliacao.
    success_url = reverse_lazy('lista_jogos')


# AvaliarJogoView: deixa uma avaliação (nota + comentário) em um jogo. Precisa estar logado.
# Roda quando acessa "/jogos/<pk>/avaliar/".
# Se a pessoa não estiver logada, o LoginRequiredMixin manda pra página de login e,
# depois de entrar, ela volta pra cá (o Django coloca ?next=/jogos/5/avaliar/ na URL do login).
class AvaliarJogoView(LoginRequiredMixin, CreateView):
    model = Avaliacao
    form_class = AvaliacaoForm
    template_name = 'catalogo/form_avaliacao.html'

    # dispatch é o primeiro método que roda na view, antes do get ou do post.
    # Busco o jogo aqui uma vez só, porque preciso dele no form_valid (pra ligar a avaliação)
    # e no get_context_data (pra mostrar o nome do jogo). Se não existir, dá 404.
    # self.kwargs são as partes da URL, então self.kwargs['pk'] é o número do <int:pk>.
    def dispatch(self, request, *args, **kwargs):
        self.jogo = get_object_or_404(Jogo, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # form_valid roda quando o is_valid() deu certo, logo antes de salvar.
    # O AvaliacaoForm não tem os campos "jogo" e "usuario", então eu coloco os dois aqui.
    # form.instance é a Avaliacao que o formulário vai salvar.
    def form_valid(self, form):
        form.instance.jogo = self.jogo
        # O usuário é sempre quem está logado. Assim ninguém consegue avaliar no nome de outra pessoa.
        form.instance.usuario = self.request.user
        # O super().form_valid() é quem salva no banco e faz o redirect pro get_success_url.
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mando o jogo porque o template mostra "Avaliar <nome do jogo>".
        context['jogo'] = self.jogo
        return context

    # Depois de avaliar, volto pro detalhe do jogo, onde a avaliação nova já aparece.
    def get_success_url(self):
        return reverse('detalhe_jogo', args=[self.jogo.pk])


# CadastroView: cria uma conta nova de usuário comum (nível "user").
# Roda quando acessa "/cadastro/".
# É uma CreateView com o UserCreationForm do Django. O usuário criado aqui tem is_staff=False,
# então ele nunca vira admin pelo site. Admin só é criado pelo createsuperuser ou pelo próprio /admin/.
class CadastroView(CreateView):
    form_class = UserCreationForm
    template_name = 'catalogo/cadastro.html'
    success_url = reverse_lazy('inicio')

    def form_valid(self, form):
        # form.save() cria o usuário no banco (com a senha criptografada) e devolve ele.
        usuario = form.save()
        # Crio o perfil junto, pra todo usuário novo já ter o seu (relação 1:1).
        Perfil.objects.create(usuario=usuario)
        # Já deixo a pessoa logada, pra ela não ter que digitar a senha de novo logo depois de cadastrar.
        login(self.request, usuario)
        return redirect(self.success_url)


# PerfilView: página "Meu perfil", onde a pessoa vê os dados dela e edita a bio e a plataforma favorita.
# Roda quando acessa "/perfil/". Precisa estar logado.
# Repara que a URL não tem id: a página sempre mostra o perfil de quem está logado.
# Assim ninguém consegue abrir ou editar o perfil de outra pessoa trocando o número na URL.
class PerfilView(LoginRequiredMixin, UpdateView):
    form_class = PerfilForm
    template_name = 'catalogo/perfil.html'
    success_url = reverse_lazy('perfil')

    # get_object: normalmente a UpdateView busca pelo pk da URL. Aqui eu troquei pra buscar
    # o perfil do usuário logado (request.user).
    # get_or_create busca o perfil e, se não existir, cria. Precisei disso porque usuários criados
    # fora do site (o admin do createsuperuser, ou um usuário criado no /admin/) não passam pela
    # CadastroView e ficam sem perfil. Ele devolve dois valores: o objeto e se foi criado agora (True/False).
    # O "_" é só um nome pra variável que eu não vou usar.
    def get_object(self, queryset=None):
        perfil, _ = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # As avaliações que essa pessoa já fez, usando o related_name='avaliacoes' do ForeignKey usuario.
        # select_related('jogo') traz o jogo de cada avaliação no mesmo SQL.
        context['minhas_avaliacoes'] = (
            self.request.user.avaliacoes.select_related('jogo').order_by('-data')
        )
        return context
