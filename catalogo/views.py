from django.shortcuts import get_object_or_404, redirect, render

from .forms import AvaliacaoForm, JogoForm
from .models import Jogo


def inicio(request):
    destaques = Jogo.objects.all().order_by('-id')[:3]
    return render(request, 'catalogo/inicio.html', {'destaques': destaques})


def lista_jogos(request):
    jogos = Jogo.objects.all().order_by('titulo')
    return render(request, 'catalogo/lista_jogos.html', {'jogos': jogos})


def detalhe_jogo(request, id):
    jogo = get_object_or_404(Jogo, id=id)
    avaliacoes = jogo.avaliacoes.all().order_by('-data')
    return render(request, 'catalogo/detalhe_jogo.html', {
        'jogo': jogo,
        'avaliacoes': avaliacoes,
    })


def novo_jogo(request):
    if request.method == 'POST':
        form = JogoForm(request.POST)
        if form.is_valid():
            jogo = form.save()
            return redirect('detalhe_jogo', id=jogo.id)
    else:
        form = JogoForm()

    return render(request, 'catalogo/form_jogo.html', {
        'form': form,
        'titulo_pagina': 'Cadastrar jogo',
    })


def editar_jogo(request, id):
    jogo = get_object_or_404(Jogo, id=id)
    # pega o título antes do is_valid(), senão aparece o título novo mesmo sem salvar
    titulo_pagina = f'Editar jogo: {jogo.titulo}'

    if request.method == 'POST':
        form = JogoForm(request.POST, instance=jogo)
        if form.is_valid():
            form.save()
            return redirect('detalhe_jogo', id=jogo.id)
    else:
        form = JogoForm(instance=jogo)

    return render(request, 'catalogo/form_jogo.html', {
        'form': form,
        'titulo_pagina': titulo_pagina,
    })


def excluir_jogo(request, id):
    jogo = get_object_or_404(Jogo, id=id)

    if request.method == 'POST':
        jogo.delete()
        return redirect('lista_jogos')

    return render(request, 'catalogo/confirmar_exclusao.html', {'jogo': jogo})


def avaliar_jogo(request, id):
    jogo = get_object_or_404(Jogo, id=id)

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.jogo = jogo
            avaliacao.save()
            return redirect('detalhe_jogo', id=jogo.id)
    else:
        form = AvaliacaoForm()

    return render(request, 'catalogo/form_avaliacao.html', {
        'form': form,
        'jogo': jogo,
    })
