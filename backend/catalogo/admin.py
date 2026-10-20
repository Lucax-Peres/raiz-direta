"""Django Admin do catálogo: painel para cadastrar e revisar os dados."""
from django.contrib import admin

from .models import Categoria, Produto, Produtor, UnidadeMedida


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "slug", "ativa"]
    list_filter = ["ativa"]
    search_fields = ["nome"]
    prepopulated_fields = {"slug": ["nome"]}


@admin.register(UnidadeMedida)
class UnidadeMedidaAdmin(admin.ModelAdmin):
    list_display = ["nome", "sigla", "permite_fracao"]
    search_fields = ["nome", "sigla"]


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 0
    fields = ["nome", "categoria", "unidade", "preco", "disponivel"]


@admin.register(Produtor)
class ProdutorAdmin(admin.ModelAdmin):
    list_display = ["nome", "responsavel", "municipio", "uf", "ativo"]
    list_filter = ["ativo", "municipio"]
    search_fields = ["nome", "responsavel", "municipio"]
    inlines = [ProdutoInline]


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ["nome", "produtor", "categoria", "unidade", "preco", "disponivel"]
    list_editable = ["preco", "disponivel"]
    list_filter = ["disponivel", "categoria", "produtor__municipio"]
    search_fields = ["nome", "produtor__nome"]
    autocomplete_fields = ["produtor", "categoria", "unidade"]
    list_select_related = ["produtor", "categoria", "unidade"]
