# Migration 0005: cria o Perfil (relação 1:1 com o usuário) e troca o nome digitado da avaliação
# (nome_usuario) por um ForeignKey pro usuário (usuario).
#
# O makemigrations sozinho não dava conta da segunda parte: o banco já tem avaliações, e o campo
# usuario é obrigatório. Se eu só criasse a coluna, o Django ia perguntar qual usuário colocar em
# todas as avaliações antigas, e eu ia perder quem escreveu cada uma. Por isso fiz em 4 passos:
#   1. cria a coluna usuario deixando vazio (null=True), pra não dar erro nas avaliações que já existem
#   2. roda uma função Python (RunPython) que liga cada avaliação a um usuário com o mesmo nome
#   3. apaga a coluna nome_usuario, que não é mais usada
#   4. deixa a coluna usuario obrigatória de novo (sem null), igual está no models.py
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# passar_nomes_para_usuarios: o passo 2. O Django chama essa função quando roda o migrate.
# "apps" são os models do jeito que estavam NESTE ponto das migrations, e não os do models.py de hoje.
# Por isso eu pego os models com apps.get_model() em vez de importar do models.py.
# "schema_editor" o Django sempre manda, mas aqui eu não uso.
def passar_nomes_para_usuarios(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Avaliacao = apps.get_model('catalogo', 'Avaliacao')

    for avaliacao in Avaliacao.objects.all():
        # O username não pode ter espaço, então "Ana Paula" vira "Ana_Paula".
        username = avaliacao.nome_usuario.strip().replace(' ', '_')[:150]
        # get_or_create: se já existe usuário com esse nome usa ele, se não cria.
        # Assim duas avaliações da "Ana" ficam com o mesmo usuário.
        # A senha '!' é o jeito do Django marcar "sem senha": ninguém consegue entrar com esse usuário.
        # Eles só existem pra guardar quem fez as avaliações de exemplo. Se precisar, o admin
        # pode definir uma senha pra eles no /admin/.
        usuario, _ = User.objects.get_or_create(username=username, defaults={'password': '!'})
        avaliacao.usuario = usuario
        avaliacao.save()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0004_alter_categoria_options_alter_plataforma_options'),
        # Depende da tabela de usuários existir, por isso o swappable_dependency do AUTH_USER_MODEL.
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Tabela nova do Perfil.
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True)),
                ('plataforma_favorita', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='perfis', to='catalogo.plataforma')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'perfil',
                'verbose_name_plural': 'perfis',
            },
        ),
        # Passo 1
        migrations.AddField(
            model_name='avaliacao',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes', to=settings.AUTH_USER_MODEL),
        ),
        # Passo 2. O segundo parâmetro (noop = "não faz nada") é o que roda se alguém desfizer a migration.
        migrations.RunPython(passar_nomes_para_usuarios, migrations.RunPython.noop),
        # Passo 3
        migrations.RemoveField(
            model_name='avaliacao',
            name='nome_usuario',
        ),
        # Passo 4
        migrations.AlterField(
            model_name='avaliacao',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes', to=settings.AUTH_USER_MODEL),
        ),
    ]
