from django.core.validators import MinValueValidator
from django.db import models


class Desenvolvedora(models.Model):
    nome = models.CharField(max_length=100)
    pais = models.CharField(max_length=50, blank=True)
    ano_fundacao = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Plataforma(models.Model):
    nome = models.CharField(max_length=50)
    fabricante = models.CharField(max_length=50)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Jogo(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    ano_lancamento = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    desenvolvedora = models.ForeignKey(Desenvolvedora, on_delete=models.PROTECT, related_name='jogos')
    plataforma = models.ForeignKey(Plataforma, on_delete=models.PROTECT, related_name='jogos')
    categorias = models.ManyToManyField(Categoria, related_name='jogos')

    def __str__(self):
        return self.titulo


class Avaliacao(models.Model):
    NOTAS = [
        (1, '1 - Péssimo'),
        (2, '2 - Ruim'),
        (3, '3 - Regular'),
        (4, '4 - Bom'),
        (5, '5 - Excelente'),
    ]

    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='avaliacoes')
    nome_usuario = models.CharField(max_length=50)
    nota = models.PositiveSmallIntegerField(choices=NOTAS)
    comentario = models.TextField(blank=True)
    data = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'avaliação'
        verbose_name_plural = 'avaliações'

    def __str__(self):
        return f'{self.jogo} - nota {self.nota} ({self.nome_usuario})'
