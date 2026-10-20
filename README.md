# Raiz Direta

Marketplace B2B que conecta pequenos e médios produtores rurais a restaurantes, mercados e hortifrutis.
Projeto acadêmico de Engenharia de Software e Extensão I (Engenharia de Computação).

> 📄 Documentação completa (instalação, arquitetura, modelo de dados, API, segurança):
> [`docs/Raiz-Direta_Documentacao-Tecnica_v1.0.pdf`](docs/Raiz-Direta_Documentacao-Tecnica_v1.0.pdf)

## Início rápido

Pré-requisitos: Docker Desktop aberto, Python 3.10+ e Git.

```bash
cp .env.example .env              # preencha senha e DJANGO_SECRET_KEY (veja a documentação)
docker compose up -d              # PostgreSQL 18 + Adminer
docker compose ps                 # "raiz-db" deve aparecer como healthy

cd backend
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py popular_dados    # dados FICTÍCIOS de demonstração
python manage.py createsuperuser
python manage.py test catalogo    # 14 testes
python manage.py runserver        # parar: Control + C
```

## Endereços

| Serviço | Endereço |
|---|---|
| Verificação da API | http://127.0.0.1:8000/api/health/ |
| API do catálogo | http://127.0.0.1:8000/api/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| Adminer (servidor: `db`) | http://localhost:8080 |

## Comandos úteis

| Comando | O que faz |
|---|---|
| `docker compose down` | Para tudo e **mantém** os dados |
| `docker compose down -v` | Para tudo e **apaga** os dados (reset total) |
| `python manage.py popular_dados --limpar` | Recria o catálogo fictício do zero |

## Problemas comuns

- **`address already in use` na 5432:** já existe outro PostgreSQL na máquina.
  Troque `POSTGRES_PORT` para `5433` no `.env` e ajuste a porta na `DATABASE_URL`.
  Para ver quem ocupa a porta: `lsof -nP -iTCP:5432 -sTCP:LISTEN`.
- **`password authentication failed` no Adminer:** confira a senha do `.env`. A senha só é aplicada
  na criação do volume; se mudou depois, rode `docker compose down -v` (apaga os dados).

⚠️ Nunca versione nem compartilhe o arquivo `.env`.
