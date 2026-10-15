# "forms" é o módulo do Django pra formulários. Ele monta o HTML dos campos,
# valida o que a pessoa digitou e mostra as mensagens de erro.
from django import forms

from .models import Avaliacao, Desenvolvedora, Jogo


# JogoForm: formulário de cadastrar e editar jogo.
# É usado nas views novo_jogo e editar_jogo. Quando eu chamo form.save(), ele retorna o Jogo salvo.
# ModelForm = formulário criado a partir de um model. O Django olha os campos do Jogo
# e já cria os campos do formulário com as validações certas (obrigatório, número, preço >= 0...).
# Assim eu não preciso repetir tudo que já está no models.py.
class JogoForm(forms.ModelForm):
    # No model, desenvolvedora é ForeignKey, e por padrão o ModelForm ia mostrar um select.
    # Eu troquei por um campo de texto pra pessoa digitar o nome e não precisar ir no admin
    # cadastrar a desenvolvedora antes. Quem transforma esse texto em Desenvolvedora é o save() lá embaixo.
    desenvolvedora = forms.CharField(max_length=100)

    # Na Meta do ModelForm eu digo qual model ele usa e quais campos entram.
    class Meta:
        model = Jogo
        # Listo os campos um por um em vez de usar '__all__', assim sei exatamente o que aparece na tela.
        # 'desenvolvedora' não está aqui porque eu criei ele na mão ali em cima.
        # Isso tem um efeito importante: como ela está fora do fields, o is_valid() só confere o campo
        # de texto (obrigatório, até 100 letras) e não copia nem valida a desenvolvedora no model.
        # Por isso não dá erro de "jogo sem desenvolvedora". Ela só é colocada no jogo lá no save().
        fields = [
            'titulo',
            'descricao',
            'ano_lancamento',
            'preco',
            'plataforma',
            'categorias',
        ]
        # labels = os textos que aparecem do lado de cada campo. Sem isso o Django usa o nome
        # do campo e sairia "Titulo" e "Preco", sem acento.
        labels = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'ano_lancamento': 'Ano de lançamento',
            'preco': 'Preço (R$)',
        }
        # widget = o tipo de elemento HTML usado pro campo.
        # O padrão do ManyToMany é uma caixa de seleção múltipla, que precisa segurar Ctrl pra
        # escolher mais de uma. Com checkboxes fica bem mais fácil marcar várias categorias.
        widgets = {
            'categorias': forms.CheckboxSelectMultiple,
        }

    # Ordem dos campos na tela. Precisei disso porque o campo desenvolvedora, que eu criei na mão,
    # ia aparecer no fim do formulário. Assim ele fica no meio, junto com os outros dados do jogo.
    field_order = ['titulo', 'descricao', 'ano_lancamento', 'preco', 'desenvolvedora', 'plataforma', 'categorias']

    # __init__ roda toda vez que o formulário é criado (JogoForm() ou JogoForm(request.POST...)).
    # Uso ele pra ajustar campos depois que o Django montou tudo.
    # *args e **kwargs pegam qualquer argumento que a view mandar (request.POST, instance=jogo...),
    # sem eu precisar listar um por um. Aí eu repasso tudo do jeito que veio pro __init__ original.
    def __init__(self, *args, **kwargs):
        # super().__init__ chama o __init__ original do ModelForm, que é quem cria os campos.
        # Precisa vir primeiro, senão self.fields ainda não existe.
        super().__init__(*args, **kwargs)
        # Troca o "---------" padrão do select por um texto em português.
        self.fields['plataforma'].empty_label = 'Selecione uma plataforma'
        # self.instance é o Jogo ligado ao formulário. Se tem pk (id), é edição de um jogo que já existe.
        # Nesse caso eu preencho o campo de texto com o nome da desenvolvedora atual,
        # porque como eu criei o campo na mão, o Django não preenche ele sozinho.
        if self.instance.pk:
            self.fields['desenvolvedora'].initial = self.instance.desenvolvedora.nome

    # save(): salva o jogo. É chamado pela view depois do is_valid().
    # Sobrescrevi pra resolver a desenvolvedora antes de salvar. Retorna o Jogo salvo.
    def save(self, commit=True):
        # cleaned_data são os dados já validados e "limpos" pelo is_valid().
        nome = self.cleaned_data['desenvolvedora']
        # Uso filter() e não get() porque o get() dá erro (DoesNotExist) quando não acha nada,
        # e aqui não achar é normal (desenvolvedora nova). O filter() devolve um QuerySet (uma lista
        # de resultados) que pode vir vazio, e o .first() pega o primeiro ou None se não tiver nenhum.
        # nome__iexact compara sem ligar pra maiúscula/minúscula, então "mojang" acha "Mojang"
        # e não cria uma desenvolvedora repetida.
        desenvolvedora = Desenvolvedora.objects.filter(nome__iexact=nome).first()
        # Se não existe ainda, crio. O create() já cria e salva no banco numa linha só.
        if desenvolvedora is None:
            desenvolvedora = Desenvolvedora.objects.create(nome=nome)

        # Coloco a desenvolvedora no jogo e deixo o save() original do ModelForm salvar o resto
        # (inclusive as categorias, que ficam na tabela do meio do ManyToMany).
        self.instance.desenvolvedora = desenvolvedora
        return super().save(commit)


# AvaliacaoForm: formulário pra avaliar um jogo. Usado na view avaliar_jogo.
# Também é ModelForm, então o save() retorna uma Avaliacao.
class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        # 'jogo' fica de fora porque a pessoa não escolhe o jogo: ele vem da URL e a view coloca
        # depois com save(commit=False). 'data' fica de fora porque o auto_now_add preenche sozinho.
        fields = ['nome_usuario', 'nota', 'comentario']
        labels = {
            'nome_usuario': 'Seu nome',
            'comentario': 'Comentário',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O Django já coloca uma opção vazia "---------" no começo do select de nota.
        # Aqui eu troco a lista inteira pra essa opção vazia ter um texto em português.
        # Como o valor dela é '', se a pessoa não escolher nenhuma nota o is_valid() dá erro de campo obrigatório.
        self.fields['nota'].choices = [('', 'Selecione uma nota')] + Avaliacao.NOTAS
