"""Testes automatizados do catálogo: regras do banco e comportamento da API."""
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Categoria, Produto, Produtor, UnidadeMedida


class BaseCatalogoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.hortalicas = Categoria.objects.create(nome="Hortaliças", slug="hortalicas")
        cls.frutas = Categoria.objects.create(nome="Frutas", slug="frutas")
        cls.kg = UnidadeMedida.objects.create(sigla="kg", nome="Quilograma", permite_fracao=True)
        cls.maco = UnidadeMedida.objects.create(sigla="maço", nome="Maço")
        cls.produtor = Produtor.objects.create(
            nome="Sítio Teste", responsavel="Fulano Teste", municipio="Cuiabá",
        )
        cls.alface = Produto.objects.create(
            produtor=cls.produtor, categoria=cls.hortalicas, unidade=cls.maco,
            nome="Alface", preco=Decimal("3.50"),
        )
        cls.manga = Produto.objects.create(
            produtor=cls.produtor, categoria=cls.frutas, unidade=cls.kg,
            nome="Manga", preco=Decimal("6.00"), disponivel=False,
        )


class RegrasDoBancoTests(BaseCatalogoTestCase):
    def test_preco_zero_e_rejeitado_pelo_banco(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Produto.objects.create(
                produtor=self.produtor, categoria=self.frutas, unidade=self.kg,
                nome="Brinde", preco=Decimal("0"),
            )

    def test_mesmo_produto_mesma_unidade_nao_duplica(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Produto.objects.create(
                produtor=self.produtor, categoria=self.hortalicas, unidade=self.maco,
                nome="Alface", preco=Decimal("4.00"),
            )

    def test_mesmo_produto_em_outra_unidade_e_permitido(self):
        Produto.objects.create(
            produtor=self.produtor, categoria=self.hortalicas, unidade=self.kg,
            nome="Alface", preco=Decimal("12.00"),
        )
        self.assertEqual(Produto.objects.filter(nome="Alface").count(), 2)

    def test_nao_apaga_produtor_com_produtos(self):
        with self.assertRaises(ProtectedError):
            self.produtor.delete()


class ApiCatalogoTests(BaseCatalogoTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_responde_ok(self):
        resposta = self.client.get("/api/health/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["banco"], "conectado")

    def test_lista_produtos_publica_e_paginada(self):
        resposta = self.client.get("/api/produtos/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["count"], 2)

    def test_filtra_por_categoria(self):
        dados = self.client.get("/api/produtos/?categoria=frutas").json()
        self.assertEqual([p["nome"] for p in dados["results"]], ["Manga"])

    def test_filtra_por_disponibilidade(self):
        dados = self.client.get("/api/produtos/?disponivel=true").json()
        self.assertEqual([p["nome"] for p in dados["results"]], ["Alface"])

    def test_busca_por_texto(self):
        dados = self.client.get("/api/produtos/?search=manga").json()
        self.assertEqual(dados["count"], 1)

    def test_ordena_por_preco_decrescente(self):
        dados = self.client.get("/api/produtos/?ordering=-preco").json()
        self.assertEqual([p["nome"] for p in dados["results"]], ["Manga", "Alface"])

    def test_produtor_inativo_some_do_catalogo(self):
        Produtor.objects.filter(pk=self.produtor.pk).update(ativo=False)
        self.assertEqual(self.client.get("/api/produtos/").json()["count"], 0)

    def test_produtores_em_ordem_alfabetica_com_contagem(self):
        Produtor.objects.create(nome="Chácara A", responsavel="X", municipio="Cuiabá")
        dados = self.client.get("/api/produtores/").json()
        self.assertEqual([p["nome"] for p in dados["results"]], ["Chácara A", "Sítio Teste"])
        self.assertEqual(dados["results"][1]["total_produtos"], 1)  # só a Alface está disponível

    def test_visitante_nao_pode_criar_produto(self):
        resposta = self.client.post("/api/produtos/", {"nome": "Invasor"}, format="json")
        self.assertIn(resposta.status_code, {401, 403})


class PopularDadosTests(TestCase):
    def test_comando_pode_rodar_duas_vezes_sem_duplicar(self):
        call_command("popular_dados", stdout=StringIO())
        primeiro = Produto.objects.count()
        call_command("popular_dados", stdout=StringIO())
        self.assertEqual(Produto.objects.count(), primeiro)
        self.assertEqual(primeiro, 20)
        self.assertTrue(all("(fictício)" in p.nome for p in Produtor.objects.all()))
