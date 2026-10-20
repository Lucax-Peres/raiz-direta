# Raiz Direta — instruções do projeto para o Claude Code

Marketplace **B2B** que conecta pequenos e médios produtores rurais (Cuiabá/MT) a compradores
profissionais (restaurantes, mercados, hortifrutis) — uma "CEASA digital".
Projeto **acadêmico** de Engenharia de Software + Extensão I (Engenharia de Computação).
Documentação completa: `docs/Raiz-Direta_Documentacao-Tecnica_v1.1.pdf`.

## Idioma e postura
- Responda sempre em **português brasileiro**; termos técnicos em inglês quando apropriado.
- Atue como engenheiro de software sênior + Scrum Master + tutor: explique o **porquê** das decisões.
- Seja crítico: aponte problemas, alternativas e riscos. Corrija o usuário quando ele estiver errado.
- **Nunca invente** evidências acadêmicas, reuniões, entrevistas, Sprints, métricas ou resultados de testes.
  Diferencie sempre: executado × planejado × simulado.
- Antes de propor funcionalidade/tecnologia nova, verifique escopo: alinhada ao propósito? necessária
  para o MVP? viável no prazo? valor proporcional à complexidade? Senão, trate como evolução futura.
- Não altere decisões já aprovadas (abaixo) sem justificar e pedir confirmação.

## Stack (decidida)
| Camada | Tecnologia |
|---|---|
| Banco | PostgreSQL 18 em Docker (`postgres:18`) + Adminer |
| Backend | Python 3.10+, **Django 5.2 LTS**, **Django REST Framework 3.18**, psycopg 3, python-dotenv |
| Frontend | Ainda não iniciado (Next.js está **em análise**, não decidido) |
| Testes | `django.test.TestCase` + `rest_framework.test.APIClient` |

## Estrutura
```
docker-compose.yml        # db (raiz-db) + adminer; portas presas a 127.0.0.1
.env / .env.example       # .env NUNCA versionado; variáveis POSTGRES_*, DJANGO_*
backend/config/           # settings.py (lê tudo do .env), urls.py, views.py (health)
backend/catalogo/         # app da Sprint 2: models, admin, serializers, views, urls, tests
backend/catalogo/management/commands/popular_dados.py   # seed FICTÍCIO idempotente
docs/                     # documentação em PDF
```

## Comandos
```bash
docker compose up -d                       # na raiz; depois: docker compose ps → raiz-db (healthy)
cd backend && source .venv/bin/activate    # sempre ativar o venv
python manage.py migrate
python manage.py popular_dados [--limpar]  # dados fictícios (5 produtores, 20 produtos)
python manage.py test catalogo -v 2        # suíte atual: 21 testes
python manage.py runserver                 # http://127.0.0.1:8000/api/  e  /admin/
python manage.py makemigrations --check --dry-run   # confirma que não há migration pendente
```

## Modelo de dados (app `catalogo`)
- `Categoria`(nome único, slug único, ativa) · `UnidadeMedida`(sigla única, nome único, permite_fracao)
- `Produtor`(nome, responsavel, municipio, uf="MT", telefone?, descricao?, ativo) — UNIQUE(nome, municipio)
- `Produto`(FK produtor/categoria/unidade com **PROTECT**, nome, descricao?, preco NUMERIC(10,2), disponivel)
  — CHECK preco > 0 · UNIQUE(produtor, nome, unidade) · índice (categoria, disponivel)
- Sem CPF/CNPJ/endereço (minimização de dados — LGPD).

## API (somente leitura nesta Sprint)
`/api/health/`, `/api/categorias/`, `/api/unidades/`, `/api/produtores/`, `/api/produtos/`.
Filtros de produtos: `categoria=<slug>`, `produtor=<id>`, `municipio=<nome>` (iexact),
`disponivel=true|false`, `search=`, `ordering=preco|-preco|nome|criado_em`. Paginação: 20.
Permissão global: `IsAuthenticatedOrReadOnly`. Cadastro/edição é feito pelo **Django Admin**.

## Convenções de código
- Nomes de domínio em **português** (modelos, campos, testes); código limpo, comentado onde há decisão.
- Regras de negócio importantes **também no banco** (constraints), não só em formulário.
- Consultas de lista: `select_related` (evitar N+1) e **`order_by` explícito** — o Django ignora
  `Meta.ordering` em consultas com agregação (`annotate/Count`), o que quebra a paginação.
- Toda regra nova → teste automatizado (padrão Arrange/Act/Assert). Rode a suíte antes de commitar.
- Mudou `models.py` → `makemigrations` e versione a migration.
- Commits no padrão **Conventional Commits** (`feat:`, `fix:`, `docs:`, `test:`, `chore:`), um assunto por commit.
- Dados de seed são **fictícios** e marcados com "(fictício)" — nunca apresentá-los como reais.

## Armadilhas conhecidas
- Na máquina do responsável, a porta 5432 é de outro PostgreSQL local → o projeto usa **5433** (`POSTGRES_PORT` no `.env`).
- Fora do Docker (Django, terminal): `localhost:<POSTGRES_PORT>`. Dentro do Docker (Adminer): host `db`, porta 5432.
- Postgres 18+: o volume é montado em `/var/lib/postgresql` (não em `/data`).
- A senha do banco só é aplicada na criação do volume; trocar exige `docker compose down -v` (apaga dados).
- `runserver` ocupa o terminal; para parar: **Control+C**.

## Segurança
- Nunca leia, imprima, copie ou commite o conteúdo do `.env` (senhas e `DJANGO_SECRET_KEY`).
- Antes de commit/push, confira que `.env`, `.venv/` e `__pycache__/` não estão no stage.
- `DEBUG=False` por padrão; `check --deploy` tem avisos esperados (HTTPS) até haver publicação.

## Scrum (Scrum Guide 2020)
Responsabilidades: Product Owner, Scrum Master, Developers (não confundir com cargos técnicos).
Artefato → compromisso: Product Backlog → Product Goal · Sprint Backlog → Sprint Goal · Increment → Definition of Done.
Story points, Planning Poker e burndown são práticas complementares, não obrigatórias.
Sprint Goal, histórias, RF/RN/RNF e DoD da Sprint 2: seção 17 do PDF (**proposta, aguardando aprovação da equipe**).

## Decisões registradas (ADR)
001 Docker só para o banco · 002 Django 5.2 LTS + DRF · 003 porta configurável (5433) ·
004 API somente leitura + cadastro via Admin na Sprint 2 · 005 regras no banco + PROTECT nas FKs.
