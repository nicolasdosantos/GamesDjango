# MinValueValidator é um "validador" do Django: ele confere se o valor não é menor que um mínimo.
# Usei no preço pra ninguém cadastrar jogo com preço negativo.
from django.core.validators import MinValueValidator
# "models" é o módulo do Django que tem a classe Model e todos os tipos de campo (CharField, ForeignKey...)
from django.db import models


# Model = uma classe Python que vira uma tabela no banco de dados.
# Cada atributo da classe vira uma coluna, e cada objeto criado vira uma linha.
# O Django cria a tabela sozinho quando eu rodo makemigrations + migrate:
# o makemigrations gera um arquivo (migration) dizendo o que mudou, e o migrate aplica isso no banco.
#
# Repara que eu não criei campo "id" em nenhum model: o Django cria sozinho uma coluna id em cada tabela.
# Ela é a chave primária (primary key), um número que aumenta sozinho (1, 2, 3...) e nunca se repete.
# É esse id que aparece na URL (/jogos/5/) e que eu uso como jogo.id. "pk" é só outro nome pro mesmo campo.

# Desenvolvedora: guarda as empresas que fazem os jogos (ex: Mojang, Nintendo).
# Ela não é chamada diretamente: o Django usa ela quando eu salvo/busco desenvolvedoras
# (no admin, no formulário de jogo, etc.). Uma desenvolvedora pode ter vários jogos.
class Desenvolvedora(models.Model):
    # CharField = texto curto. O max_length é o tamanho máximo do texto.
    # Quem barra texto maior que isso é a validação do Django: o formulário dá erro e o campo HTML
    # ganha maxlength. O SQLite não confere tamanho de texto, então esse limite não vem do banco.
    # (Nesta versão do Django, com SQLite, o max_length nem é obrigatório, mas em bancos como o MySQL é.
    # Eu coloquei sempre pra deixar claro o limite de cada campo.)
    nome = models.CharField(max_length=100)
    # blank=True deixa o campo vazio no formulário, porque nem sempre eu sei o país.
    pais = models.CharField(max_length=50, blank=True)
    # PositiveIntegerField = número inteiro que não pode ser negativo (ano não é negativo).
    # Coloquei null=True E blank=True porque é número: blank deixa o formulário passar vazio
    # e null deixa o banco guardar "nada" (NULL). Em texto só blank já basta, porque fica "".
    ano_fundacao = models.PositiveIntegerField(null=True, blank=True)

    # __str__ define como o objeto aparece escrito, por exemplo na lista do admin, no select de
    # desenvolvedora da tela de jogo do admin e quando eu faço {{ jogo.desenvolvedora }} no template.
    # (No formulário do site a desenvolvedora é um campo de texto e não um select, ver forms.py.)
    # Sem isso ia aparecer "Desenvolvedora object (1)", que não ajuda ninguém.
    # Retorna o nome da desenvolvedora.
    def __str__(self):
        return self.nome


# Categoria: os gêneros dos jogos (Ação, RPG, Aventura...).
# Um jogo pode ter várias categorias e uma categoria pode ter vários jogos (relação N:N, explico lá no Jogo).
class Categoria(models.Model):
    # unique=True impede duas categorias com o mesmo nome (não faz sentido ter "RPG" duas vezes).
    nome = models.CharField(max_length=50, unique=True)
    # TextField = texto longo, sem limite de tamanho. Bom pra descrição.
    descricao = models.TextField(blank=True)

    # A classe Meta guarda configurações do model que não são colunas.
    # ordering = ['nome'] faz toda busca de categorias já vir em ordem alfabética,
    # assim eu não preciso ficar colocando order_by() em todo lugar.
    class Meta:
        ordering = ['nome']

    # Retorna o nome da categoria pra aparecer legível no admin e nos formulários.
    def __str__(self):
        return self.nome


# Plataforma: onde o jogo roda (PC, PlayStation 5, Switch...).
# Cada jogo tem UMA plataforma e uma plataforma tem vários jogos (1:N).
class Plataforma(models.Model):
    nome = models.CharField(max_length=50)
    # fabricante é obrigatório (sem blank=True), toda plataforma tem quem fabrica (Sony, Nintendo...).
    fabricante = models.CharField(max_length=50)

    # Mesma ideia da Categoria: lista sempre em ordem alfabética.
    class Meta:
        ordering = ['nome']

    # Retorna o nome da plataforma.
    def __str__(self):
        return self.nome


# Jogo: é o model principal do projeto, o catálogo gira em torno dele.
# É usado nas views de listar, ver detalhe, criar, editar e excluir jogo.
# Ele se liga com Desenvolvedora, Plataforma e Categoria.
class Jogo(models.Model):
    titulo = models.CharField(max_length=100)
    # Descrição é obrigatória (não tem blank=True), todo jogo precisa de um resumo.
    descricao = models.TextField()
    ano_lancamento = models.PositiveIntegerField()
    # DecimalField = número com casas decimais exatas. Usei ele e não FloatField porque
    # float pode dar erro de arredondamento (tipo 59.9 virar 59.899999), e com dinheiro isso é ruim.
    # max_digits=8 é o total de dígitos e decimal_places=2 são os centavos (até 999999.99).
    # O MinValueValidator(0) barra preço negativo quando o formulário é validado (is_valid() no site ou no admin).
    # Ele NÃO roda num save() direto: um Jogo.objects.create(preco=-5) no código salvaria, porque o save()
    # não valida e o banco não tem essa regra. Por isso a migration 0002 não mudou nada no banco.
    preco = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    # ForeignKey = chave estrangeira, uma relação com outra tabela.
    # No banco vira uma coluna "desenvolvedora_id" que guarda o id da desenvolvedora.
    # É 1:N: uma desenvolvedora tem vários jogos, mas cada jogo tem uma desenvolvedora só.
    # on_delete=PROTECT: se eu tentar apagar uma desenvolvedora que ainda tem jogos, o Django NÃO deixa.
    # Escolhi isso pra não sumir jogo do catálogo sem querer (com CASCADE os jogos iam junto).
    # related_name='jogos' é o nome do "caminho de volta": com ele eu posso fazer
    # desenvolvedora.jogos.all() pra pegar todos os jogos de uma desenvolvedora.
    desenvolvedora = models.ForeignKey(Desenvolvedora, on_delete=models.PROTECT, related_name='jogos')
    # Mesma lógica: cada jogo tem uma plataforma e o PROTECT não deixa apagar plataforma com jogo ligado.
    plataforma = models.ForeignKey(Plataforma, on_delete=models.PROTECT, related_name='jogos')
    # ManyToManyField = relação N:N (muitos pra muitos): um jogo tem várias categorias
    # e uma categoria tem vários jogos. Uma coluna só não resolve isso, então o Django cria
    # sozinho uma tabela do meio que liga os ids dos jogos com os ids das categorias.
    # Por isso eu não precisei criar essa tabela na mão.
    categorias = models.ManyToManyField(Categoria, related_name='jogos')

    # Retorna o título do jogo. Aparece no admin e também na Avaliacao, que usa o jogo no __str__ dela.
    def __str__(self):
        return self.titulo


# Avaliacao: guarda as notas e comentários que as pessoas deixam em um jogo.
# É criada pela view avaliar_jogo e mostrada na página de detalhe do jogo.
class Avaliacao(models.Model):
    # Lista de opções pra nota. Cada item é (valor salvo no banco, texto que aparece pro usuário).
    # No banco fica só o número (1 a 5), e na tela aparece "4 - Bom", por exemplo.
    NOTAS = [
        (1, '1 - Péssimo'),
        (2, '2 - Ruim'),
        (3, '3 - Regular'),
        (4, '4 - Bom'),
        (5, '5 - Excelente'),
    ]

    # Cada avaliação é de um jogo, e um jogo pode ter várias avaliações (1:N).
    # on_delete=CASCADE: se o jogo for apagado, as avaliações dele vão junto.
    # Aqui faz sentido ser diferente do PROTECT, porque avaliação sem jogo não serve pra nada.
    # Com related_name='avaliacoes' eu faço jogo.avaliacoes.all() na view de detalhe.
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='avaliacoes')
    # O projeto não tem login, então a pessoa só digita o nome dela.
    nome_usuario = models.CharField(max_length=50)
    # PositiveSmallIntegerField = inteiro positivo pequeno, que basta pra uma nota de 1 a 5.
    # choices=NOTAS faz o formulário mostrar um select com só essas 5 opções,
    # e o is_valid() recusa qualquer valor fora da lista (tipo nota 10 ou 0).
    nota = models.PositiveSmallIntegerField(choices=NOTAS)
    comentario = models.TextField(blank=True)
    # DateField = data (sem hora). auto_now_add=True preenche sozinho com a data de hoje
    # quando a avaliação é criada, e o usuário nem vê esse campo no formulário.
    data = models.DateField(auto_now_add=True)

    # verbose_name é o nome que aparece no admin. Sem isso ia aparecer "Avaliacaos",
    # porque o Django só coloca um "s" no final. Assim fica certo, com acento.
    class Meta:
        verbose_name = 'avaliação'
        verbose_name_plural = 'avaliações'

    # Retorna algo como "Minecraft - nota 5 (João)". O {self.jogo} usa o __str__ do Jogo.
    def __str__(self):
        return f'{self.jogo} - nota {self.nota} ({self.nome_usuario})'
