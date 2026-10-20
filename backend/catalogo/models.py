"""
Modelo de dados do catálogo do Raiz Direta (Sprint 2).

Escopo: produtores ofertam produtos, organizados por categoria e vendidos
em uma unidade de comercialização. Pedidos, estoque, frete e pagamento
ficam FORA deste escopo (ainda não aprovados).
"""
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    """Base abstrata: registra quando cada linha foi criada e alterada."""

    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True


class Categoria(TimeStampedModel):
    """Agrupamento de produtos (ex.: Hortaliças, Frutas)."""

    nome = models.CharField("nome", max_length=60, unique=True)
    slug = models.SlugField(
        "slug", max_length=60, unique=True,
        help_text="Identificador usado na URL e nos filtros (ex.: hortalicas).",
    )
    descricao = models.TextField("descrição", blank=True)
    ativa = models.BooleanField("ativa", default=True)

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class UnidadeMedida(TimeStampedModel):
    """Unidade em que um produto é comercializado (kg, maço, dúzia...)."""

    sigla = models.CharField("sigla", max_length=10, unique=True)
    nome = models.CharField("nome", max_length=40, unique=True)
    permite_fracao = models.BooleanField(
        "permite fração", default=False,
        help_text="Marque se a unidade aceita quantidades fracionadas (ex.: 2,5 kg).",
    )

    class Meta:
        verbose_name = "unidade de medida"
        verbose_name_plural = "unidades de medida"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.sigla})"


class Produtor(TimeStampedModel):
    """Pequeno ou médio produtor rural que oferta produtos na plataforma."""

    nome = models.CharField(
        "nome da propriedade", max_length=120,
        help_text="Nome comercial exibido no catálogo (ex.: Sítio Boa Vista).",
    )
    responsavel = models.CharField("responsável", max_length=120)
    municipio = models.CharField("município", max_length=80)
    uf = models.CharField("UF", max_length=2, default="MT")
    telefone = models.CharField("telefone", max_length=20, blank=True)
    descricao = models.TextField("descrição", blank=True)
    ativo = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "produtor"
        verbose_name_plural = "produtores"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["nome", "municipio"], name="produtor_nome_municipio_unico",
            ),
        ]

    def __str__(self):
        return f"{self.nome} — {self.municipio}/{self.uf}"


class Produto(TimeStampedModel):
    """Oferta de um produtor: um item, em uma unidade, por um preço."""

    produtor = models.ForeignKey(
        Produtor, on_delete=models.PROTECT, related_name="produtos",
        verbose_name="produtor",
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="produtos",
        verbose_name="categoria",
    )
    unidade = models.ForeignKey(
        UnidadeMedida, on_delete=models.PROTECT, related_name="produtos",
        verbose_name="unidade",
    )
    nome = models.CharField("nome", max_length=120)
    descricao = models.TextField("descrição", blank=True)
    preco = models.DecimalField(
        "preço (R$)", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    disponivel = models.BooleanField(
        "disponível", default=True,
        help_text="Desmarque quando o produto estiver fora de época ou esgotado.",
    )

    class Meta:
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        ordering = ["nome"]
        constraints = [
            # Regra garantida pelo PRÓPRIO banco, não só pelo formulário.
            models.CheckConstraint(condition=Q(preco__gt=0), name="produto_preco_positivo"),
            # O mesmo produtor não anuncia o mesmo item duas vezes na mesma unidade.
            models.UniqueConstraint(
                fields=["produtor", "nome", "unidade"], name="produto_unico_por_produtor_unidade",
            ),
        ]
        indexes = [
            models.Index(fields=["categoria", "disponivel"], name="produto_cat_disp_idx"),
        ]

    def __str__(self):
        return f"{self.nome} ({self.unidade.sigla}) — {self.produtor.nome}"
