from django import forms

from .models import Avaliacao, Categoria, Desenvolvedora, Jogo, Perfil, Plataforma


# ModelForm: gera os campos a partir do model Jogo e já traz as validações dele
# (campo obrigatório, tamanho máximo, preço não negativo...)
class JogoForm(forms.ModelForm):
    # desenvolvedora é digitada em texto em vez de escolhida numa lista
    desenvolvedora = forms.CharField(max_length=100)

    class Meta:
        model = Jogo
        fields = [
            'titulo',
            'descricao',
            'ano_lancamento',
            'preco',
            'plataforma',
            'categorias',
        ]
        labels = {
            'titulo': 'Título',
            'descricao': 'Descrição',
            'ano_lancamento': 'Ano de lançamento',
            'preco': 'Preço (R$)',
        }
        widgets = {
            'categorias': forms.CheckboxSelectMultiple,
        }

    field_order = ['titulo', 'descricao', 'ano_lancamento', 'preco', 'desenvolvedora', 'plataforma', 'categorias']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plataforma'].empty_label = 'Selecione uma plataforma'
        # na edição já mostra o nome da desenvolvedora atual
        if self.instance.pk:
            self.fields['desenvolvedora'].initial = self.instance.desenvolvedora.nome

    # usa a desenvolvedora se já existir (iexact = igual, sem ligar pra maiúscula), senão cria;
    # depois o super().save() salva o jogo e as categorias
    def save(self, commit=True):
        nome = self.cleaned_data['desenvolvedora']
        desenvolvedora = Desenvolvedora.objects.filter(nome__iexact=nome).first()
        if desenvolvedora is None:
            desenvolvedora = Desenvolvedora.objects.create(nome=nome)

        self.instance.desenvolvedora = desenvolvedora
        return super().save(commit)


# formulário de avaliação: só nota e comentário, o jogo e o usuário a view preenche
class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        labels = {
            'comentario': 'Comentário',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nota'].choices = [('', 'Selecione uma nota')] + Avaliacao.NOTAS


# formulário do perfil
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['bio', 'plataforma_favorita']
        labels = {
            'bio': 'Sobre você',
            'plataforma_favorita': 'Plataforma favorita',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plataforma_favorita'].empty_label = 'Nenhuma'


# filtros da lista de jogos: é forms.Form (não ModelForm) porque não salva nada,
# só valida o que veio pela URL
# todos os campos são opcionais: o que ficar vazio não filtra
class FiltroJogoForm(forms.Form):
    # as chaves batem com o ORDENACOES do views.py
    ORDENS = [
        ('titulo', 'Título (A-Z)'),
        ('menor_preco', 'Menor preço'),
        ('maior_preco', 'Maior preço'),
        ('recentes', 'Lançamento mais recente'),
        ('nota', 'Mais bem avaliados'),
    ]
    NOTAS_MINIMAS = [
        ('', 'Qualquer nota'),
        ('2', '2 ou mais'),
        ('3', '3 ou mais'),
        ('4', '4 ou mais'),
        ('5', 'Só nota 5'),
    ]

    # max_length evita busca gigante
    busca = forms.CharField(
        required=False, max_length=100, label='Buscar',
        widget=forms.TextInput(attrs={'placeholder': 'Título ou desenvolvedora (ex: zelda, nintendo)'}),
    )
    # ModelChoiceField já valida se o id existe no banco
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(), required=False, empty_label='Todas'
    )
    plataforma = forms.ModelChoiceField(
        queryset=Plataforma.objects.all(), required=False, empty_label='Todas'
    )
    desenvolvedora = forms.ModelChoiceField(
        queryset=Desenvolvedora.objects.order_by('nome'), required=False, empty_label='Todas'
    )
    # localize aceita preço com vírgula (59,90)
    preco_min = forms.DecimalField(
        required=False, localize=True, max_digits=8, decimal_places=2,
        min_value=0, max_value=999999.99, label='Preço de (R$)',
    )
    preco_max = forms.DecimalField(
        required=False, localize=True, max_digits=8, decimal_places=2,
        min_value=0, max_value=999999.99, label='Preço até (R$)',
    )
    ano_min = forms.IntegerField(
        required=False, min_value=1950, max_value=2100, label='Lançado a partir de',
    )
    # coerce=int converte a opção escolhida pra número
    nota_min = forms.TypedChoiceField(
        choices=NOTAS_MINIMAS, coerce=int, empty_value=None, required=False, label='Nota média',
    )
    ordem = forms.ChoiceField(choices=ORDENS, required=False, label='Ordenar por')

    # clean() roda depois de validar cada campo; validação que compara dois campos fica aqui
    def clean(self):
        dados = super().clean()
        preco_min = dados.get('preco_min')
        preco_max = dados.get('preco_max')
        if preco_min is not None and preco_max is not None and preco_min > preco_max:
            self.add_error('preco_max', 'O preço máximo não pode ser menor que o mínimo.')
        return dados
