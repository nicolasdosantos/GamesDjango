from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import AvaliacaoForm, FiltroJogoForm, JogoForm, PerfilForm
from .models import Avaliacao, Jogo, Perfil


# nível admin: antes da view rodar, o UserPassesTestMixin chama o test_func()
# se der False: user logado recebe 403 (Acesso negado) e visitante vai pro login
# é um mixin, então é só colocar ele antes da view (ex: NovoJogoView)
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# página inicial com os 3 últimos jogos (maior id = cadastrado por último)
class InicioView(TemplateView):
    template_name = 'catalogo/inicio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destaques'] = Jogo.objects.all().order_by('-id')[:3]
        return context


# opções de ordenação; o título entra como desempate quando o valor é igual
ORDENACOES = {
    'titulo': ['titulo'],
    'menor_preco': ['preco', 'titulo'],
    'maior_preco': ['-preco', 'titulo'],
    'recentes': ['-ano_lancamento', 'titulo'],
    'nota': ['-media', 'titulo'],
}


# lista de jogos com filtros e paginação
class ListaJogosView(ListView):
    model = Jogo
    template_name = 'catalogo/lista_jogos.html'
    context_object_name = 'jogos'
    paginate_by = 9  # 9 jogos por página

    # get_queryset define quais jogos a ListView mostra; cada filter() vai acrescentando
    # condições no WHERE e a consulta só roda no banco quando o template usa os jogos
    def get_queryset(self):
        # select_related traz desenvolvedora e plataforma junto (JOIN), prefetch_related busca as categorias
        # de uma vez só (N:N); sem isso seria uma consulta a mais pra cada jogo
        # annotate cria o campo 'media' com a média das notas de cada jogo (AVG no SQL)
        jogos = (
            Jogo.objects.select_related('desenvolvedora', 'plataforma')
            .prefetch_related('categorias')
            .annotate(media=Avg('avaliacoes__nota'))
        )

        # o formulário de filtro é GET, então os valores vêm na URL (?busca=zelda&preco_max=100)
        # e o Django coloca eles no request.GET
        self.form_filtro = FiltroJogoForm(self.request.GET)
        # se um campo vier inválido ele fica fora do cleaned_data e os outros filtros continuam valendo
        self.form_filtro.is_valid()
        dados = self.form_filtro.cleaned_data

        # icontains = "contém", sem diferenciar maiúscula (LIKE no SQL)
        # o Q permite usar OU (|): a palavra pode estar no título OU na desenvolvedora
        # como é um filter por palavra, todas as palavras precisam bater (E)
        busca = dados.get('busca')
        if busca:
            for palavra in busca.split():
                jogos = jogos.filter(
                    Q(titulo__icontains=palavra) | Q(desenvolvedora__nome__icontains=palavra)
                )
        # categoria é N:N, então filtra pela tabela do meio
        if dados.get('categoria'):
            jogos = jogos.filter(categorias=dados['categoria'])
        if dados.get('plataforma'):
            jogos = jogos.filter(plataforma=dados['plataforma'])
        if dados.get('desenvolvedora'):
            jogos = jogos.filter(desenvolvedora=dados['desenvolvedora'])
        # "is not None" porque 0 também é um valor válido
        if dados.get('preco_min') is not None:
            jogos = jogos.filter(preco__gte=dados['preco_min'])
        if dados.get('preco_max') is not None:
            jogos = jogos.filter(preco__lte=dados['preco_max'])
        if dados.get('ano_min') is not None:
            jogos = jogos.filter(ano_lancamento__gte=dados['ano_min'])
        # media é o campo criado no annotate lá em cima
        if dados.get('nota_min') is not None:
            jogos = jogos.filter(media__gte=dados['nota_min'])

        # sem ordem escolhida, ordena por título
        ordem = dados.get('ordem') or 'titulo'
        return jogos.order_by(*ORDENACOES[ordem])

    # get_page trata página inválida (?page=abc ou 999) mostrando a primeira/última em vez de erro 404
    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(queryset, page_size)
        pagina = paginator.get_page(self.request.GET.get('page'))
        return paginator, pagina, pagina.object_list, pagina.has_other_pages()

    # get_context_data manda variáveis extras pro template; aqui vai o form pra tela
    # mostrar os filtros que a pessoa já escolheu
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_filtro'] = self.form_filtro
        return context


# DetailView: pega o pk da URL (/jogos/5/), busca o jogo e dá 404 se não existir
class DetalheJogoView(DetailView):
    model = Jogo
    template_name = 'catalogo/detalhe_jogo.html'
    context_object_name = 'jogo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # jogo.avaliacoes funciona por causa do related_name do ForeignKey
        context['avaliacoes'] = self.object.avaliacoes.select_related('usuario').order_by('-data')
        return context


# CRUD de jogo (só admin, por causa do AdminRequiredMixin)
# Create: no GET mostra o formulário vazio; no POST os dados vão no corpo da requisição
# (não aparecem na URL), o Django lê em request.POST, valida com is_valid() e,
# se estiver tudo certo, salva no banco com form.save() e redireciona
# se tiver erro, mostra o formulário de novo com as mensagens
class NovoJogoView(AdminRequiredMixin, CreateView):
    model = Jogo
    form_class = JogoForm
    template_name = 'catalogo/form_jogo.html'
    extra_context = {'titulo_pagina': 'Cadastrar jogo'}

    # depois de salvar redireciona (assim um F5 não manda o POST de novo)
    # self.object é o jogo que acabou de ser criado
    def get_success_url(self):
        return reverse('detalhe_jogo', args=[self.object.pk])


# Update: igual ao Create, mas busca o jogo pelo pk da URL e o formulário já vem preenchido;
# no POST ele altera o registro que já existe (UPDATE) em vez de criar outro
class EditarJogoView(AdminRequiredMixin, UpdateView):
    model = Jogo
    form_class = JogoForm
    template_name = 'catalogo/form_jogo.html'

    # guarda o título original pra mostrar no topo da página
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


# Delete: no GET mostra a página de confirmação; só apaga no POST (botão Excluir)
# assim ninguém apaga um jogo só abrindo um link
class ExcluirJogoView(AdminRequiredMixin, DeleteView):
    model = Jogo
    template_name = 'catalogo/confirmar_exclusao.html'
    context_object_name = 'jogo'
    # reverse_lazy porque aqui é atributo da classe e as URLs ainda não foram carregadas
    success_url = reverse_lazy('lista_jogos')


# avaliar um jogo: LoginRequiredMixin manda pro login quem não está logado,
# com ?next= na URL pra voltar pra cá depois de entrar
class AvaliarJogoView(LoginRequiredMixin, CreateView):
    model = Avaliacao
    form_class = AvaliacaoForm
    template_name = 'catalogo/form_avaliacao.html'

    # dispatch é o primeiro método que roda (no GET e no POST), então o jogo já fica
    # disponível pro resto da view; get_object_or_404 dá 404 se o jogo não existir
    def dispatch(self, request, *args, **kwargs):
        self.jogo = get_object_or_404(Jogo, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # form_valid roda depois do is_valid() dar certo, antes de salvar
    # o jogo e o usuário não vêm do formulário (senão daria pra avaliar no nome de outro),
    # a view preenche com o jogo da URL e o usuário logado
    def form_valid(self, form):
        form.instance.jogo = self.jogo
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jogo'] = self.jogo
        return context

    def get_success_url(self):
        return reverse('detalhe_jogo', args=[self.jogo.pk])


# cadastro de usuário: o UserCreationForm já valida senha e confirmação e salva a senha
# criptografada; quem se cadastra aqui é sempre user comum (is_staff fica False)
class CadastroView(CreateView):
    form_class = UserCreationForm
    template_name = 'catalogo/cadastro.html'
    success_url = reverse_lazy('inicio')

    def form_valid(self, form):
        # salva o usuário, cria o perfil dele (1:1) e já deixa logado
        usuario = form.save()
        Perfil.objects.create(usuario=usuario)
        login(self.request, usuario)
        return redirect(self.success_url)


# perfil do usuário logado
class PerfilView(LoginRequiredMixin, UpdateView):
    form_class = PerfilForm
    template_name = 'catalogo/perfil.html'
    success_url = reverse_lazy('perfil')

    # a URL /perfil/ não tem id: o perfil é sempre o de quem está logado (request.user),
    # então não dá pra editar o de outra pessoa; get_or_create cria se ainda não existir
    def get_object(self, queryset=None):
        perfil, _ = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['minhas_avaliacoes'] = (
            self.request.user.avaliacoes.select_related('jogo').order_by('-data')
        )
        return context
