"""
Popula o catálogo com DADOS FICTÍCIOS para desenvolvimento e demonstração.

Todos os produtores são inventados (marcados com "(fictício)") e os preços
são ilustrativos. NÃO representam produtores, parcerias ou preços reais.

Uso:
    python manage.py popular_dados            # cria/atualiza (pode rodar várias vezes)
    python manage.py popular_dados --limpar   # apaga o catálogo e recria do zero
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogo.models import Categoria, Produto, Produtor, UnidadeMedida

CATEGORIAS = [
    ("Hortaliças", "hortalicas", "Folhas e legumes frescos."),
    ("Frutas", "frutas", "Frutas da estação e regionais."),
    ("Raízes e Tubérculos", "raizes-e-tuberculos", "Mandioca, batata-doce e similares."),
    ("Ovos", "ovos", "Ovos caipiras e de granja."),
    ("Temperos e Ervas", "temperos-e-ervas", "Cheiro-verde, pimentas e ervas."),
]

UNIDADES = [
    ("kg", "Quilograma", True),
    ("maço", "Maço", False),
    ("dz", "Dúzia", False),
    ("un", "Unidade", False),
    ("cx", "Caixa", False),
]

PRODUTORES = [
    ("Sítio Boa Esperança (fictício)", "Ana Exemplo", "Cuiabá",
     "Hortaliças cultivadas sem agrotóxicos."),
    ("Chácara Recanto Verde (fictício)", "Carlos Exemplo", "Várzea Grande",
     "Produção familiar de frutas e legumes."),
    ("Sítio Serra Azul (fictício)", "Beatriz Exemplo", "Chapada dos Guimarães",
     "Frutas regionais e ovos caipiras."),
    ("Fazendinha Rio Claro (fictício)", "Daniel Exemplo", "Santo Antônio de Leverger",
     "Raízes, tubérculos e temperos."),
    ("Horta Comunitária Exemplo (fictício)", "Elisa Exemplo", "Nossa Senhora do Livramento",
     "Cooperativa de pequenos produtores."),
]

# (produtor_idx, nome, categoria_slug, unidade_sigla, preço, disponível)
PRODUTOS = [
    (0, "Alface crespa", "hortalicas", "maço", "3.50", True),
    (0, "Rúcula", "hortalicas", "maço", "4.00", True),
    (0, "Couve-manteiga", "hortalicas", "maço", "3.00", True),
    (0, "Cheiro-verde", "temperos-e-ervas", "maço", "2.50", True),
    (1, "Tomate", "hortalicas", "kg", "7.90", True),
    (1, "Pepino", "hortalicas", "kg", "5.50", True),
    (1, "Banana-nanica", "frutas", "kg", "4.80", True),
    (1, "Mamão formosa", "frutas", "kg", "5.20", False),
    (2, "Pequi", "frutas", "kg", "12.00", False),
    (2, "Manga", "frutas", "kg", "6.00", True),
    (2, "Ovos caipiras", "ovos", "dz", "14.00", True),
    (2, "Maracujá", "frutas", "kg", "8.50", True),
    (3, "Mandioca", "raizes-e-tuberculos", "kg", "4.20", True),
    (3, "Batata-doce", "raizes-e-tuberculos", "kg", "5.00", True),
    (3, "Pimenta-de-cheiro", "temperos-e-ervas", "kg", "18.00", True),
    (3, "Abóbora cabotiá", "hortalicas", "kg", "4.50", True),
    (4, "Quiabo", "hortalicas", "kg", "9.00", True),
    (4, "Maxixe", "hortalicas", "kg", "10.00", True),
    (4, "Jiló", "hortalicas", "kg", "8.00", True),
    (4, "Ovos de granja", "ovos", "cx", "22.00", True),
]


class Command(BaseCommand):
    help = "Popula o catálogo com dados FICTÍCIOS para desenvolvimento e demonstração."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar", action="store_true",
            help="Apaga todos os dados do catálogo antes de popular.",
        )

    @transaction.atomic  # tudo ou nada: se algo falhar, nada é gravado
    def handle(self, *args, **options):
        if options["limpar"]:
            Produto.objects.all().delete()
            Produtor.objects.all().delete()
            Categoria.objects.all().delete()
            UnidadeMedida.objects.all().delete()
            self.stdout.write(self.style.WARNING("Catálogo apagado."))

        categorias = {}
        for nome, slug, descricao in CATEGORIAS:
            categorias[slug], _ = Categoria.objects.update_or_create(
                slug=slug, defaults={"nome": nome, "descricao": descricao, "ativa": True},
            )

        unidades = {}
        for sigla, nome, fracao in UNIDADES:
            unidades[sigla], _ = UnidadeMedida.objects.update_or_create(
                sigla=sigla, defaults={"nome": nome, "permite_fracao": fracao},
            )

        produtores = []
        for nome, responsavel, municipio, descricao in PRODUTORES:
            produtor, _ = Produtor.objects.update_or_create(
                nome=nome, municipio=municipio,
                defaults={"responsavel": responsavel, "uf": "MT",
                          "descricao": descricao, "ativo": True},
            )
            produtores.append(produtor)

        for idx, nome, cat, sigla, preco, disponivel in PRODUTOS:
            Produto.objects.update_or_create(
                produtor=produtores[idx], nome=nome, unidade=unidades[sigla],
                defaults={"categoria": categorias[cat], "preco": Decimal(preco),
                          "disponivel": disponivel},
            )

        self.stdout.write(self.style.SUCCESS(
            f"Catálogo pronto: {Categoria.objects.count()} categorias, "
            f"{UnidadeMedida.objects.count()} unidades, {Produtor.objects.count()} produtores, "
            f"{Produto.objects.count()} produtos (dados FICTÍCIOS)."
        ))
