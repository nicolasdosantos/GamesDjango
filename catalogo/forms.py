from django import forms

from .models import Avaliacao, Desenvolvedora, Jogo


class JogoForm(forms.ModelForm):
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
        if self.instance.pk:
            self.fields['desenvolvedora'].initial = self.instance.desenvolvedora.nome

    def save(self, commit=True):
        nome = self.cleaned_data['desenvolvedora']
        desenvolvedora = Desenvolvedora.objects.filter(nome__iexact=nome).first()
        if desenvolvedora is None:
            desenvolvedora = Desenvolvedora.objects.create(nome=nome)

        self.instance.desenvolvedora = desenvolvedora
        return super().save(commit)


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nome_usuario', 'nota', 'comentario']
        labels = {
            'nome_usuario': 'Seu nome',
            'comentario': 'Comentário',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nota'].choices = [('', 'Selecione uma nota')] + Avaliacao.NOTAS
