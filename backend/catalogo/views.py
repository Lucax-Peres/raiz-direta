"""
Endpoints do catálogo (somente leitura).

Cadastro e edição acontecem pelo Django Admin nesta Sprint, pois ainda não
há tela de login. Endpoints de escrita entram junto com a autenticação.
"""
from django.db.models import Count, Q
from rest_framework import filters, viewsets

from .models import Categoria, Produto, Produtor, UnidadeMedida
from .serializers import (
    CategoriaSerializer,
    ProdutorSerializer,
    ProdutoSerializer,
    UnidadeMedidaSerializer,
)


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.filter(ativa=True)
    pagination_class = None  # lista curta: usada em menus/filtros


class UnidadeMedidaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UnidadeMedidaSerializer
    queryset = UnidadeMedida.objects.all()
    pagination_class = None


class ProdutorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProdutorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nome", "municipio"]

    def get_queryset(self):
        # order_by explícito: o Django IGNORA o Meta.ordering em consultas com
        # agregação (Count). Sem ordem fixa, a paginação pode repetir/pular itens.
        return (
            Produtor.objects.filter(ativo=True)
            .annotate(total_produtos=Count("produtos", filter=Q(produtos__disponivel=True)))
            .order_by("nome")
        )


class ProdutoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Filtros por query string:
      ?categoria=<slug>  ?produtor=<id>  ?municipio=<nome>
      ?disponivel=true|false  ?search=<texto>  ?ordering=preco|-preco|nome
    """

    serializer_class = ProdutoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nome", "descricao", "produtor__nome"]
    ordering_fields = ["preco", "nome", "criado_em"]
    ordering = ["nome"]  # ordem padrão quando ?ordering não é informado

    def get_queryset(self):
        # select_related evita o problema N+1 (uma consulta extra por produto).
        qs = Produto.objects.select_related("produtor", "categoria", "unidade").filter(
            produtor__ativo=True, categoria__ativa=True,
        )
        params = self.request.query_params
        if categoria := params.get("categoria"):
            qs = qs.filter(categoria__slug=categoria)
        if (produtor := params.get("produtor")) and produtor.isdigit():
            qs = qs.filter(produtor_id=int(produtor))
        if municipio := params.get("municipio"):
            qs = qs.filter(produtor__municipio__iexact=municipio)
        disponivel = params.get("disponivel", "").lower()
        if disponivel in {"true", "false"}:
            qs = qs.filter(disponivel=(disponivel == "true"))
        return qs
