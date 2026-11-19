from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# empresa que fez o jogo
class Desenvolvedora(models.Model):
    nome = models.CharField(max_length=100)
    pais = models.CharField(max_length=50, blank=True)
    ano_fundacao = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.nome


# gênero do jogo (ação, rpg...)
class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


# onde o jogo roda (PC, PS5...)
class Plataforma(models.Model):
    nome = models.CharField(max_length=50)
    fabricante = models.CharField(max_length=50)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


# cada model vira uma tabela e cada atributo vira uma coluna (o id o Django cria sozinho)
class Jogo(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    ano_lancamento = models.PositiveIntegerField()
    # Decimal em vez de float pra não dar erro de arredondamento; o validator barra preço negativo
    preco = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    # 1:N - cada jogo tem uma desenvolvedora e uma plataforma (vira a coluna desenvolvedora_id)
    # PROTECT não deixa apagar desenvolvedora/plataforma que ainda tem jogo
    # related_name permite fazer desenvolvedora.jogos.all()
    desenvolvedora = models.ForeignKey(Desenvolvedora, on_delete=models.PROTECT, related_name='jogos')
    plataforma = models.ForeignKey(Plataforma, on_delete=models.PROTECT, related_name='jogos')
    # N:N - um jogo tem várias categorias e uma categoria tem vários jogos
    # o Django cria sozinho a tabela do meio (catalogo_jogo_categorias)
    categorias = models.ManyToManyField(Categoria, related_name='jogos')

    def __str__(self):
        return self.titulo


# nota e comentário de um usuário sobre um jogo
class Avaliacao(models.Model):
    NOTAS = [
        (1, '1 - Péssimo'),
        (2, '2 - Ruim'),
        (3, '3 - Regular'),
        (4, '4 - Bom'),
        (5, '5 - Excelente'),
    ]

    # 1:N - CASCADE: apagou o jogo ou o usuário, apaga as avaliações
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='avaliacoes')
    nota = models.PositiveSmallIntegerField(choices=NOTAS)
    comentario = models.TextField(blank=True)
    data = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'avaliação'
        verbose_name_plural = 'avaliações'

    def __str__(self):
        return f'{self.jogo} - nota {self.nota} ({self.usuario})'


# dados extras do usuário (1 perfil por usuário)
class Perfil(models.Model):
    # 1:1 - cada usuário tem um perfil só
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    bio = models.TextField(blank=True)
    # SET_NULL: se a plataforma for apagada o perfil fica sem favorita
    plataforma_favorita = models.ForeignKey(
        Plataforma, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfis'
    )

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'Perfil de {self.usuario}'
