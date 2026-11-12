# tests.py: testes automáticos. São classes que herdam de TestCase e rodam com
# "python manage.py test catalogo". O Django cria um banco de teste separado (test_gamedex),
# roda os testes e apaga ele no final, então não mexe nos dados de verdade.
# Testei aqui principalmente os níveis de acesso e os filtros, que são as partes mais fáceis de quebrar.

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Avaliacao, Categoria, Desenvolvedora, Jogo, Perfil, Plataforma


class GameDexTestCase(TestCase):
    # setUp roda antes de CADA teste e cria os dados que os testes usam.
    def setUp(self):
        self.admin = User.objects.create_user('chefe', password='senha-teste-123', is_staff=True)
        self.comum = User.objects.create_user('jogador', password='senha-teste-123')

        nintendo = Desenvolvedora.objects.create(nome='Nintendo')
        mojang = Desenvolvedora.objects.create(nome='Mojang')
        switch = Plataforma.objects.create(nome='Switch', fabricante='Nintendo')
        pc = Plataforma.objects.create(nome='PC', fabricante='Vários')
        self.rpg = Categoria.objects.create(nome='RPG')

        self.zelda = Jogo.objects.create(
            titulo='Zelda', descricao='Aventura', ano_lancamento=2017,
            preco=300, desenvolvedora=nintendo, plataforma=switch,
        )
        self.zelda.categorias.add(self.rpg)
        self.minecraft = Jogo.objects.create(
            titulo='Minecraft', descricao='Blocos', ano_lancamento=2011,
            preco=100, desenvolvedora=mojang, plataforma=pc,
        )


class NiveisDeAcessoTest(GameDexTestCase):
    def test_visitante_ve_a_lista(self):
        resposta = self.client.get(reverse('lista_jogos'))
        self.assertEqual(resposta.status_code, 200)

    def test_visitante_vai_pro_login_ao_editar(self):
        resposta = self.client.get(reverse('editar_jogo', args=[self.zelda.pk]))
        # 302 = redirecionamento. Tem que mandar pra página de login.
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('login'), resposta.url)

    def test_user_comum_nao_pode_cadastrar_editar_nem_excluir(self):
        self.client.login(username='jogador', password='senha-teste-123')
        self.assertEqual(self.client.get(reverse('novo_jogo')).status_code, 403)
        self.assertEqual(self.client.get(reverse('editar_jogo', args=[self.zelda.pk])).status_code, 403)
        # Mesmo mandando o POST direto (sem passar pela tela), o jogo não pode ser apagado.
        self.assertEqual(self.client.post(reverse('excluir_jogo', args=[self.zelda.pk])).status_code, 403)
        self.assertTrue(Jogo.objects.filter(pk=self.zelda.pk).exists())

    def test_admin_pode_excluir(self):
        self.client.login(username='chefe', password='senha-teste-123')
        resposta = self.client.post(reverse('excluir_jogo', args=[self.zelda.pk]))
        self.assertRedirects(resposta, reverse('lista_jogos'))
        self.assertFalse(Jogo.objects.filter(pk=self.zelda.pk).exists())

    def test_avaliacao_fica_no_nome_de_quem_esta_logado(self):
        self.client.login(username='jogador', password='senha-teste-123')
        # Tento mandar um "usuario" diferente no POST. O form ignora porque esse campo não está nele.
        self.client.post(reverse('avaliar_jogo', args=[self.zelda.pk]), {
            'nota': 5, 'comentario': 'Muito bom', 'usuario': self.admin.pk,
        })
        avaliacao = Avaliacao.objects.get()
        self.assertEqual(avaliacao.usuario, self.comum)
        self.assertEqual(avaliacao.jogo, self.zelda)


class CadastroEPerfilTest(GameDexTestCase):
    def test_cadastro_cria_usuario_comum_com_perfil(self):
        self.client.post(reverse('cadastro'), {
            'username': 'novato', 'password1': 'UmaSenhaBoa#2026', 'password2': 'UmaSenhaBoa#2026',
        })
        novato = User.objects.get(username='novato')
        self.assertFalse(novato.is_staff)
        # relação 1:1: o perfil existe e é acessado por usuario.perfil
        self.assertTrue(Perfil.objects.filter(usuario=novato).exists())

    def test_perfil_edita_so_o_proprio(self):
        self.client.login(username='jogador', password='senha-teste-123')
        self.client.post(reverse('perfil'), {'bio': 'Gosto de RPG', 'plataforma_favorita': ''})
        self.assertEqual(self.comum.perfil.bio, 'Gosto de RPG')
        self.assertFalse(Perfil.objects.filter(usuario=self.admin).exists())


class FiltrosTest(GameDexTestCase):
    # Função auxiliar: faz a busca e devolve a lista de títulos que apareceu.
    def buscar(self, **filtros):
        resposta = self.client.get(reverse('lista_jogos'), filtros)
        return [jogo.titulo for jogo in resposta.context['jogos']]

    def test_sem_filtro_mostra_todos(self):
        self.assertEqual(self.buscar(), ['Minecraft', 'Zelda'])

    def test_filtro_por_titulo_sem_ligar_pra_maiuscula(self):
        self.assertEqual(self.buscar(titulo='zel'), ['Zelda'])

    def test_filtro_por_categoria(self):
        self.assertEqual(self.buscar(categoria=self.rpg.pk), ['Zelda'])

    def test_filtro_por_preco_maximo(self):
        self.assertEqual(self.buscar(preco_max='150'), ['Minecraft'])

    def test_filtro_invalido_nao_quebra_a_pagina(self):
        resposta = self.client.get(reverse('lista_jogos'), {'categoria': 'abc', 'preco_max': 'xyz'})
        self.assertEqual(resposta.status_code, 200)
