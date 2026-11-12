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

    def test_busca_por_titulo_sem_ligar_pra_maiuscula(self):
        self.assertEqual(self.buscar(busca='zel'), ['Zelda'])

    def test_busca_tambem_procura_na_desenvolvedora(self):
        self.assertEqual(self.buscar(busca='mojang'), ['Minecraft'])

    def test_busca_por_palavras_fora_de_ordem(self):
        self.assertEqual(self.buscar(busca='nintendo zelda'), ['Zelda'])

    def test_filtro_por_categoria(self):
        self.assertEqual(self.buscar(categoria=self.rpg.pk), ['Zelda'])

    def test_preco_com_virgula(self):
        self.assertEqual(self.buscar(preco_max='150,50'), ['Minecraft'])

    def test_faixa_de_preco(self):
        self.assertEqual(self.buscar(preco_min='150', preco_max='300'), ['Zelda'])

    def test_preco_minimo_maior_que_maximo_da_erro(self):
        resposta = self.client.get(reverse('lista_jogos'), {'preco_min': '300', 'preco_max': '100'})
        self.assertIn('preco_max', resposta.context['form_filtro'].errors)

    def test_campo_invalido_nao_derruba_os_outros_filtros(self):
        # categoria=abc é inválida, mas o filtro de preço tem que continuar valendo
        self.assertEqual(self.buscar(categoria='abc', preco_max='150'), ['Minecraft'])

    def test_busca_gigante_e_recusada(self):
        resposta = self.client.get(reverse('lista_jogos'), {'busca': 'x' * 5000})
        self.assertIn('busca', resposta.context['form_filtro'].errors)

    def test_ordenar_por_maior_preco(self):
        self.assertEqual(self.buscar(ordem='maior_preco'), ['Zelda', 'Minecraft'])

    def test_ordem_que_nao_existe_usa_titulo(self):
        self.assertEqual(self.buscar(ordem='password'), ['Minecraft', 'Zelda'])

    def test_filtro_por_nota_media(self):
        Avaliacao.objects.create(jogo=self.zelda, usuario=self.comum, nota=5)
        Avaliacao.objects.create(jogo=self.minecraft, usuario=self.comum, nota=2)
        self.assertEqual(self.buscar(nota_min='4'), ['Zelda'])

    def test_pagina_invalida_nao_da_erro(self):
        for pagina in ['abc', '999']:
            resposta = self.client.get(reverse('lista_jogos'), {'page': pagina})
            self.assertEqual(resposta.status_code, 200)

    def test_paginacao_mantem_os_filtros(self):
        # cria jogos a mais pra passar dos 9 por página
        for numero in range(10):
            Jogo.objects.create(
                titulo=f'Teste {numero}', descricao='x', ano_lancamento=2020, preco=10,
                desenvolvedora=self.zelda.desenvolvedora, plataforma=self.zelda.plataforma,
            )
        resposta = self.client.get(reverse('lista_jogos'), {'busca': 'teste'})
        # o link da página 2 tem que levar a busca junto
        self.assertContains(resposta, '?busca=teste&amp;page=2')
