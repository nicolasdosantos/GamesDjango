# Do django.shortcuts vêm três atalhos que uso em quase toda view:
# - render: junta um template HTML com os dados e devolve a página pronta
# - redirect: manda o navegador pra outra URL (usando o name que está no urls.py)
# - get_object_or_404: busca um objeto no banco e, se não achar, mostra erro 404 (página não encontrada)
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AvaliacaoForm, JogoForm
from .models import Jogo


# View = função que recebe um pedido do navegador (o "request") e devolve uma resposta (uma página).
# Essa resposta é um HttpResponse. O render() monta um com o HTML pronto, e o redirect() monta
# um que manda o navegador ir pra outro endereço (código 302).
# O urls.py é quem decide qual view roda pra cada endereço.
# Todas as views aqui são funções (FBV, function-based views), que é o jeito mais simples de fazer.


# inicio: página inicial do site.
# Roda quando a pessoa acessa "/" (a raiz do site).
# Retorna o template inicio.html com os 3 jogos mais recentes.
def inicio(request):
    # Jogo.objects é o "gerenciador" do model, é por ele que o ORM faz as buscas no banco.
    # ORM = o Django traduz esse código Python pra SQL, então eu não escrevo SQL na mão.
    # O resultado é um QuerySet, que é tipo uma lista de jogos vinda do banco.
    # order_by('-id'): o "-" é ordem decrescente, então o id maior (cadastrado por último) vem primeiro.
    # [:3] limita a 3 resultados. O Django transforma isso em LIMIT 3 no SQL e não traz todos os jogos.
    destaques = Jogo.objects.all().order_by('-id')[:3]
    # O dicionário é o "contexto": as variáveis que o template vai poder usar.
    # Lá no HTML eu acesso com {{ destaques }} ou {% for jogo in destaques %}.
    return render(request, 'catalogo/inicio.html', {'destaques': destaques})


# lista_jogos: mostra todos os jogos do catálogo.
# Roda quando acessa "/jogos/".
# Retorna o template lista_jogos.html com os jogos em ordem alfabética.
def lista_jogos(request):
    # all() traz todos os registros e order_by('titulo') ordena de A a Z.
    jogos = Jogo.objects.all().order_by('titulo')
    return render(request, 'catalogo/lista_jogos.html', {'jogos': jogos})


# detalhe_jogo: mostra a página de um jogo específico com as avaliações dele.
# Roda quando acessa "/jogos/<id>/", tipo "/jogos/5/".
# O "id" vem da própria URL: o <int:id> do urls.py pega o número e passa pra cá.
# Retorna o template detalhe_jogo.html com o jogo e as avaliações.
def detalhe_jogo(request, id):
    # Usei get_object_or_404 e não Jogo.objects.get() porque o get() dá erro 500 (erro do servidor)
    # quando o jogo não existe, por exemplo se alguém digitar /jogos/999/.
    # Com o get_object_or_404 aparece só "página não encontrada", que é o certo nesse caso.
    # Usei get e não filter porque quero UM jogo só. O filter() sempre devolve um QuerySet (uma lista).
    jogo = get_object_or_404(Jogo, id=id)
    # jogo.avaliacoes funciona por causa do related_name='avaliacoes' que coloquei no ForeignKey do model Avaliacao.
    # Ele traz só as avaliações DESTE jogo, e o '-data' deixa as mais novas primeiro.
    avaliacoes = jogo.avaliacoes.all().order_by('-data')
    return render(request, 'catalogo/detalhe_jogo.html', {
        'jogo': jogo,
        'avaliacoes': avaliacoes,
    })


# novo_jogo: cadastra um jogo novo.
# Roda quando acessa "/jogos/novo/". A mesma view cuida de duas situações:
# - GET (a pessoa só abriu a página): mostra o formulário vazio
# - POST (a pessoa clicou em salvar): valida os dados e salva no banco
# Se salvar, redireciona pra página do jogo novo. Se não, mostra o form_jogo.html de novo.
def novo_jogo(request):
    # request.method diz se o pedido foi GET ou POST.
    # Formulário que muda dados no banco usa POST, por isso o form do template tem method="post".
    if request.method == 'POST':
        # request.POST tem tudo que a pessoa digitou no formulário.
        # Passo isso pro JogoForm pra ele conferir e preencher os campos.
        form = JogoForm(request.POST)
        # is_valid() roda todas as validações: campo obrigatório vazio, preço negativo
        # (por causa do MinValueValidator no model), número no lugar errado, etc.
        if form.is_valid():
            # Como o JogoForm é um ModelForm, o save() cria o Jogo no banco e devolve o objeto criado.
            # Preciso dele pra saber o id do jogo novo.
            jogo = form.save()
            # Depois de salvar eu uso redirect e não render. Assim, se a pessoa apertar F5,
            # o navegador não reenvia o formulário e não cadastra o jogo duas vezes.
            # 'detalhe_jogo' é o name da URL no urls.py, e o Django monta o endereço sozinho (/jogos/<id>/).
            return redirect('detalhe_jogo', id=jogo.id)
        # Se o form for inválido, não entra no if e cai no render lá embaixo.
        # O form vai junto com as mensagens de erro e com o que a pessoa já tinha digitado.
    else:
        # GET: só abriu a página, então mando um formulário vazio.
        form = JogoForm()

    # O mesmo template serve pra cadastrar e editar, só muda o título da página.
    return render(request, 'catalogo/form_jogo.html', {
        'form': form,
        'titulo_pagina': 'Cadastrar jogo',
    })


# editar_jogo: altera um jogo que já existe.
# Roda quando acessa "/jogos/<id>/editar/".
# Funciona igual ao novo_jogo, mas o formulário já vem preenchido com os dados do jogo.
# Se salvar, redireciona pro detalhe do jogo. Se não, mostra o formulário de novo.
def editar_jogo(request, id):
    # aqui eu pego o jogo pela URL pra saber qual vou editar (e dá 404 se não existir)
    jogo = get_object_or_404(Jogo, id=id)
    # pega o título antes do is_valid(), senão aparece o título novo mesmo sem salvar
    # (o is_valid() copia pro objeto jogo, na memória, os campos que passaram na validação, mesmo quando
    # outro campo deu erro. Ele só não salva no banco. Então se a pessoa mudasse o título e errasse o preço,
    # jogo.titulo já seria o título novo e a página ia mostrar "Editar jogo: <título que nem foi salvo>")
    titulo_pagina = f'Editar jogo: {jogo.titulo}'

    if request.method == 'POST':
        # O instance=jogo é o que faz ser uma edição e não um cadastro novo.
        # Sem ele, o form.save() ia criar um segundo jogo em vez de atualizar este.
        form = JogoForm(request.POST, instance=jogo)
        if form.is_valid():
            # Aqui não preciso guardar o retorno, porque já tenho o jogo e o id dele não muda.
            form.save()
            return redirect('detalhe_jogo', id=jogo.id)
    else:
        # GET: o instance=jogo faz o formulário abrir já preenchido com os dados atuais.
        form = JogoForm(instance=jogo)

    return render(request, 'catalogo/form_jogo.html', {
        'form': form,
        'titulo_pagina': titulo_pagina,
    })


# excluir_jogo: apaga um jogo.
# Roda quando acessa "/jogos/<id>/excluir/".
# - GET: mostra uma página perguntando "tem certeza?"
# - POST: apaga de verdade e volta pra lista de jogos
def excluir_jogo(request, id):
    jogo = get_object_or_404(Jogo, id=id)

    # Só apago no POST, nunca no GET. Se apagasse no GET, bastava abrir o link
    # (ou clicar sem querer) pra perder o jogo. Com a página de confirmação a pessoa precisa
    # clicar no botão, e esse formulário ainda tem o {% csrf_token %} que protege contra pedido falso.
    if request.method == 'POST':
        # delete() remove o jogo do banco. As avaliações dele vão junto por causa do
        # on_delete=CASCADE que está no model Avaliacao.
        jogo.delete()
        # O jogo não existe mais, então não dá pra ir pro detalhe dele. Volto pra lista.
        return redirect('lista_jogos')

    # Se chegou aqui é GET, então mostro a página de confirmação.
    return render(request, 'catalogo/confirmar_exclusao.html', {'jogo': jogo})


# avaliar_jogo: deixa uma avaliação (nota + comentário) em um jogo.
# Roda quando acessa "/jogos/<id>/avaliar/".
# Se salvar, volta pro detalhe do jogo, onde a avaliação nova já aparece.
# Se não, mostra o form_avaliacao.html de novo com os erros.
def avaliar_jogo(request, id):
    # Busco o jogo pela URL, porque a avaliação precisa saber de qual jogo ela é.
    jogo = get_object_or_404(Jogo, id=id)

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            # O AvaliacaoForm não tem o campo "jogo" (a pessoa não escolhe o jogo, ele vem da URL).
            # Se eu desse save() direto ia dar erro, porque o jogo é obrigatório no banco.
            # commit=False cria o objeto Avaliacao mas ainda não salva no banco.
            avaliacao = form.save(commit=False)
            # Aí eu ligo a avaliação ao jogo certo...
            avaliacao.jogo = jogo
            # ...e só agora salvo de verdade. A data entra sozinha por causa do auto_now_add.
            avaliacao.save()
            return redirect('detalhe_jogo', id=jogo.id)
    else:
        form = AvaliacaoForm()

    # Mando o jogo junto porque o template mostra "Avaliar <nome do jogo>".
    return render(request, 'catalogo/form_avaliacao.html', {
        'form': form,
        'jogo': jogo,
    })
