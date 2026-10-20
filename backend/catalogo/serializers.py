"""Conversão dos modelos para JSON (contratos da API do catálogo)."""
from rest_framework import serializers

from .models import Categoria, Produto, Produtor, UnidadeMedida


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome", "slug", "descricao"]


class UnidadeMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = ["id", "sigla", "nome", "permite_fracao"]


class ProdutorResumoSerializer(serializers.ModelSerializer):
    """Versão curta do produtor, usada dentro de cada produto."""

    class Meta:
        model = Produtor
        fields = ["id", "nome", "municipio", "uf"]


class ProdutorSerializer(serializers.ModelSerializer):
    total_produtos = serializers.IntegerField(read_only=True)

    class Meta:
        model = Produtor
        fields = ["id", "nome", "responsavel", "municipio", "uf", "descricao", "total_produtos"]


class ProdutoSerializer(serializers.ModelSerializer):
    produtor = ProdutorResumoSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    unidade = UnidadeMedidaSerializer(read_only=True)

    class Meta:
        model = Produto
        fields = ["id", "nome", "descricao", "preco", "disponivel", "produtor", "categoria", "unidade"]
