# Raiz Direta

Marketplace B2B que conecta pequenos e médios produtores rurais a restaurantes, mercados e hortifrutis.
Projeto acadêmico de Engenharia de Software e Extensão I (Engenharia de Computação).

## Como rodar o banco de dados (desenvolvimento)

Pré-requisito: Docker Desktop aberto e rodando.

```bash
cp .env.example .env        # só na primeira vez; depois troque a senha no .env
docker compose up -d        # sobe PostgreSQL 18 + Adminer
docker compose ps           # o serviço "db" deve aparecer como healthy
```

- **Adminer** (interface web do banco): http://localhost:8080
  - Sistema: PostgreSQL · Servidor: `db` · Usuário/Senha/Base: os valores do `.env`

### Comandos úteis

| Comando | O que faz |
|---|---|
| `docker compose logs -f db` | Acompanha os logs do banco |
| `docker compose exec db psql -U raiz -d raiz_direta` | Abre o terminal SQL |
| `docker compose down` | Para tudo e **mantém** os dados |
| `docker compose down -v` | Para tudo e **apaga** os dados (reset total) |

### Problemas comuns

- **`port is already allocated` / `address already in use` na 5432:** já existe outro PostgreSQL na máquina.
  Troque `POSTGRES_PORT` para `5433` no `.env` e ajuste a porta na `DATABASE_URL`.
  Para ver quem ocupa a porta: `lsof -nP -iTCP:5432 -sTCP:LISTEN`.
