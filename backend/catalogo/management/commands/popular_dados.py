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

# Recorte geográfico do seed: somente a Baixada Cuiabana. Definição adotada: a da Embrapa
# (Região Metropolitana do Vale do Rio Cuiabá + entorno metropolitano = 13 municípios).
# Outras fontes usam recortes diferentes (ex.: algumas incluem Campo Verde).
MUNICIPIOS_BAIXADA_CUIABANA = {
    # Região Metropolitana do Vale do Rio Cuiabá
    "Cuiabá", "Várzea Grande", "Nossa Senhora do Livramento", "Santo Antônio de Leverger",
    # Entorno metropolitano
    "Acorizal", "Barão de Melgaço", "Chapada dos Guimarães", "Jangada", "Nobres",
    "Nova Brasilândia", "Planalto da Serra", "Poconé", "Rosário Oeste",
}

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
    # --- Ampliação da base (09/11/2026): mais produtores para demonstrar filtros e paginação ---
    ("Sítio Três Irmãos (fictício)", "Fernanda Exemplo", "Cuiabá",
     "Folhosas e ervas em cultivo hidropônico."),
    ("Chácara Bom Jardim (fictício)", "Gabriel Exemplo", "Várzea Grande",
     "Legumes e temperos para restaurantes."),
    ("Sítio Água Fria (fictício)", "Helena Exemplo", "Chapada dos Guimarães",
     "Frutas nativas do Cerrado."),
    ("Sítio Pantaneiro (fictício)", "Igor Exemplo", "Poconé",
     "Mandioca, banana-da-terra e frutas de quintal."),
    ("Chácara Santa Luzia (fictício)", "Joana Exemplo", "Barão de Melgaço",
     "Ovos caipiras, milho verde e abóboras."),
    ("Sítio Vale do Coxipó (fictício)", "Lucas Exemplo", "Cuiabá",
     "Hortaliças de folha e cheiro-verde."),
    ("Fazendinha Pé de Serra (fictício)", "Marina Exemplo", "Rosário Oeste",
     "Bananas, citros e raízes."),
    ("Sítio Ipê Amarelo (fictício)", "Nelson Exemplo", "Acorizal",
     "Pomar de manga, goiaba e acerola."),
    ("Chácara Raio de Sol (fictício)", "Olívia Exemplo", "Jangada",
     "Legumes de ciclo curto."),
    ("Sítio Bela Vista (fictício)", "Paulo Exemplo", "Planalto da Serra",
     "Raízes e hortaliças."),
    ("Associação de Produtores Exemplo (fictício)", "Quitéria Exemplo", "Nossa Senhora do Livramento",
     "Associação que reúne a produção de várias famílias."),
    ("Sítio Cachoeira (fictício)", "Rafael Exemplo", "Nobres",
     "Abacaxi, mamão e melancia."),
    ("Chácara Flor do Campo (fictício)", "Sílvia Exemplo", "Nova Brasilândia",
     "Hortaliças e ovos de granja."),
    ("Sítio Recanto do Cerrado (fictício)", "Tiago Exemplo", "Santo Antônio de Leverger",
     "Raízes, tubérculos e especiarias."),
    ("Horta Escola Exemplo (fictício)", "Úrsula Exemplo", "Várzea Grande",
     "Horta comunitária ligada a um projeto educativo."),
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

    # --- Ampliação da base (09/11/2026). Preços ILUSTRATIVOS, não são cotações reais. ---
    # Novos itens dos produtores originais
    (0, "Alface americana", "hortalicas", "maço", "4.00", True),
    (0, "Espinafre", "hortalicas", "maço", "5.00", True),
    (1, "Tomate", "hortalicas", "cx", "85.00", True),  # mesmo item, outra unidade (permitido)
    (1, "Berinjela", "hortalicas", "kg", "6.50", True),
    (2, "Mangaba", "frutas", "kg", "15.00", False),
    (2, "Goiaba", "frutas", "kg", "7.00", True),
    (3, "Inhame", "raizes-e-tuberculos", "kg", "7.50", True),
    (3, "Açafrão-da-terra", "temperos-e-ervas", "kg", "25.00", True),
    (4, "Abobrinha", "hortalicas", "kg", "6.00", True),
    (4, "Cebolinha", "temperos-e-ervas", "maço", "2.50", True),
    # 5 · Sítio Três Irmãos (Cuiabá)
    (5, "Alface crespa", "hortalicas", "maço", "3.80", True),
    (5, "Alface crespa", "hortalicas", "cx", "38.00", True),
    (5, "Alface roxa", "hortalicas", "maço", "4.20", True),
    (5, "Rúcula", "hortalicas", "maço", "4.50", True),
    (5, "Agrião", "hortalicas", "maço", "5.00", True),
    (5, "Manjericão", "temperos-e-ervas", "maço", "4.00", True),
    # 6 · Chácara Bom Jardim (Várzea Grande)
    (6, "Tomate cereja", "hortalicas", "kg", "14.00", True),
    (6, "Pimentão verde", "hortalicas", "kg", "9.50", True),
    (6, "Cebolinha", "temperos-e-ervas", "maço", "2.80", True),
    (6, "Salsinha", "temperos-e-ervas", "maço", "2.80", True),
    (6, "Berinjela", "hortalicas", "kg", "6.00", True),
    (6, "Chuchu", "hortalicas", "kg", "4.00", True),
    # 7 · Sítio Água Fria (Chapada dos Guimarães)
    (7, "Pequi", "frutas", "dz", "10.00", True),
    (7, "Cagaita", "frutas", "kg", "16.00", False),
    (7, "Castanha de baru", "frutas", "kg", "70.00", True),
    (7, "Mangaba", "frutas", "kg", "14.00", True),
    (7, "Maracujá-do-mato", "frutas", "kg", "12.00", False),
    (7, "Abacate", "frutas", "kg", "7.50", True),
    # 8 · Sítio Pantaneiro (Poconé)
    (8, "Mandioca", "raizes-e-tuberculos", "kg", "3.80", True),
    (8, "Banana-da-terra", "frutas", "kg", "6.50", True),
    (8, "Limão-taiti", "frutas", "kg", "5.00", True),
    (8, "Abóbora moranga", "hortalicas", "kg", "3.50", True),
    (8, "Melancia", "frutas", "un", "18.00", True),
    # 9 · Chácara Santa Luzia (Barão de Melgaço)
    (9, "Ovos caipiras", "ovos", "dz", "15.00", True),
    (9, "Ovos caipiras", "ovos", "cx", "140.00", True),
    (9, "Abóbora cabotiá", "hortalicas", "kg", "4.00", True),
    (9, "Milho verde", "hortalicas", "dz", "12.00", True),
    (9, "Quiabo", "hortalicas", "kg", "8.50", True),
    # 10 · Sítio Vale do Coxipó (Cuiabá)
    (10, "Couve-manteiga", "hortalicas", "maço", "3.20", True),
    (10, "Almeirão", "hortalicas", "maço", "3.50", True),
    (10, "Hortelã", "temperos-e-ervas", "maço", "3.50", True),
    (10, "Coentro", "temperos-e-ervas", "maço", "2.80", True),
    (10, "Cheiro-verde", "temperos-e-ervas", "maço", "2.60", True),
    (10, "Pimenta-de-cheiro", "temperos-e-ervas", "kg", "16.00", True),
    # 11 · Fazendinha Pé de Serra (Rosário Oeste)
    (11, "Banana-prata", "frutas", "kg", "5.50", True),
    (11, "Banana-nanica", "frutas", "cx", "60.00", True),
    (11, "Laranja-pera", "frutas", "kg", "3.80", True),
    (11, "Mandioca", "raizes-e-tuberculos", "kg", "3.50", True),
    (11, "Cará", "raizes-e-tuberculos", "kg", "6.00", True),
    # 12 · Sítio Ipê Amarelo (Acorizal)
    (12, "Manga palmer", "frutas", "kg", "5.50", True),
    (12, "Caju", "frutas", "kg", "9.00", False),
    (12, "Acerola", "frutas", "kg", "10.00", True),
    (12, "Goiaba", "frutas", "kg", "6.50", True),
    (12, "Limão-cravo", "frutas", "kg", "6.00", True),
    # 13 · Chácara Raio de Sol (Jangada)
    (13, "Pepino japonês", "hortalicas", "kg", "6.50", True),
    (13, "Abobrinha", "hortalicas", "kg", "5.50", True),
    (13, "Vagem", "hortalicas", "kg", "11.00", True),
    (13, "Jiló", "hortalicas", "kg", "7.50", True),
    (13, "Maxixe", "hortalicas", "kg", "9.50", True),
    # 14 · Sítio Bela Vista (Planalto da Serra)
    (14, "Batata-inglesa", "raizes-e-tuberculos", "kg", "5.20", True),
    (14, "Cenoura", "raizes-e-tuberculos", "kg", "4.80", True),
    (14, "Beterraba", "raizes-e-tuberculos", "kg", "5.00", True),
    (14, "Repolho", "hortalicas", "un", "6.00", True),
    (14, "Brócolis", "hortalicas", "un", "7.50", True),
    # 15 · Associação de Produtores Exemplo (Nossa Senhora do Livramento)
    (15, "Alface crespa", "hortalicas", "maço", "3.20", True),
    (15, "Couve-manteiga", "hortalicas", "maço", "2.80", True),
    (15, "Mandioca", "raizes-e-tuberculos", "kg", "4.00", True),
    (15, "Banana-maçã", "frutas", "kg", "7.00", True),
    (15, "Ovos caipiras", "ovos", "dz", "13.50", True),
    (15, "Pimenta-malagueta", "temperos-e-ervas", "kg", "20.00", True),
    # 16 · Sítio Cachoeira (Nobres)
    (16, "Abacaxi pérola", "frutas", "un", "7.00", True),
    (16, "Mamão papaia", "frutas", "un", "4.50", True),
    (16, "Maracujá", "frutas", "kg", "7.50", True),
    (16, "Melancia", "frutas", "un", "20.00", True),
    (16, "Laranja-pera", "frutas", "kg", "3.50", False),
    # 17 · Chácara Flor do Campo (Nova Brasilândia)
    (17, "Alface americana", "hortalicas", "maço", "4.50", True),
    (17, "Repolho roxo", "hortalicas", "un", "7.00", True),
    (17, "Couve-flor", "hortalicas", "un", "8.00", True),
    (17, "Rabanete", "raizes-e-tuberculos", "maço", "4.00", True),
    (17, "Ovos de granja", "ovos", "dz", "9.50", True),
    (17, "Ovos de granja", "ovos", "cx", "22.50", True),
    # 18 · Sítio Recanto do Cerrado (Santo Antônio de Leverger)
    (18, "Mandioca", "raizes-e-tuberculos", "kg", "3.90", True),
    (18, "Batata-doce", "raizes-e-tuberculos", "kg", "4.50", True),
    (18, "Inhame", "raizes-e-tuberculos", "kg", "7.00", True),
    (18, "Cará", "raizes-e-tuberculos", "kg", "5.80", False),
    (18, "Gengibre", "temperos-e-ervas", "kg", "22.00", True),
    (18, "Açafrão-da-terra", "temperos-e-ervas", "kg", "24.00", True),
    # 19 · Horta Escola Exemplo (Várzea Grande)
    (19, "Alface crespa", "hortalicas", "maço", "3.00", True),
    (19, "Rúcula", "hortalicas", "maço", "3.80", True),
    (19, "Espinafre", "hortalicas", "maço", "4.50", False),
    (19, "Tomate", "hortalicas", "kg", "7.00", True),
    (19, "Cheiro-verde", "temperos-e-ervas", "maço", "2.30", True),
    (19, "Hortelã", "temperos-e-ervas", "maço", "3.00", True),
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
