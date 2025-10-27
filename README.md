# Gerenciamento de Produtos — FastAPI + Streamlit + PostgreSQL (Docker & Poetry)

Projeto **full-stack** para CRUD de produtos, com:

- **Backend**: FastAPI + SQLAlchemy + Psycopg2
- **Frontend**: Streamlit
- **Banco**: PostgreSQL 18
- **Orquestração**: Docker Compose  
- **Dev/Testes locais**: Poetry (ambiente virtual e dependências)

> Status atual: CRUD funcional, Swagger no backend e UI Streamlit no frontend.

---

## Índice

- [Arquitetura & Estrutura](#arquitetura--estrutura)
- [Pré-requisitos](#pré-requisitos)
- [Subir com Docker (recomendado)](#subir-com-docker-recomendado)
- [Acessos rápidos](#acessos-rápidos)
- [Uso local com Poetry (sem Docker)](#uso-local-com-poetry-sem-docker)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Modelo de dados](#modelo-de-dados)
- [API – Endpoints](#api--endpoints)
- [Fluxos comuns via cURL](#fluxos-comuns-via-curl)
- [Dicas de desenvolvimento](#dicas-de-desenvolvimento)
- [Solução de problemas](#solução-de-problemas)
- [Próximos passos (Roadmap)](#próximos-passos-roadmap)
- [Licença](#licença)

---

## Arquitetura & Estrutura

```
projeto_python/
├─ docker-compose.yml
├─ README.md
├─ pyproject.toml             # usado com Poetry para dev/testes locais
├─ poetry.lock
├─ .python-version            # versão do Python utilizada localmente
├─ backend/
│  ├─ main.py                 # FastAPI app (inclui router)
│  ├─ models.py               # SQLAlchemy models
│  ├─ crud.py                 # lógica de acesso a dados
│  ├─ router.py               # rotas /products
│  ├─ database.py             # engine, SessionLocal, Base
│  ├─ schemas.py              # Pydantic v2
│  ├─ requirements.txt        # deps para build da imagem
│  └─ Dockerfile
└─ frontend/
   ├─ app.py                  # Streamlit UI
   ├─ requirements.txt        # deps para build da imagem
   ├─ .streamlit/
   │  └─ config.toml          # tema do Streamlit
   └─ Dockerfile
```

**Portas:**
- Backend FastAPI: `8000`
- Frontend Streamlit: `8501`
- Postgres: `5432` (exposto apenas dentro da rede do Compose)

---

## Pré-requisitos

- Docker + Docker Compose
- (Opcional para dev local) **Poetry** ≥ 1.6 e Python 3.9/3.10/3.11 (conforme seu `.python-version`)

---

## Subir com Docker (recomendado)

> A imagem oficial do **PostgreSQL 18** usa **`/var/lib/postgresql`** (sem `/data`). O `docker-compose.yml` já está ajustado.

```bash
# build e sobe tudo
docker compose up -d --build

# ver logs
docker compose logs -f postgres
docker compose logs -f backend
docker compose logs -f frontend
```

### Observações importantes (PostgreSQL 18+)

- Se trocar de versão ou já tiver um volume antigo em `/var/lib/postgresql/data`, **zerar o volume** costuma ser mais simples em dev:
  ```bash
  docker compose down -v
  docker compose up -d --build
  ```
- Para preservar dados, use `pg_dump/pg_restore` entre versões.

---

## Acessos rápidos

- **Frontend** (Streamlit): http://localhost:8501  
- **API Docs** (FastAPI/Swagger): http://localhost:8000/docs  
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Uso local com **Poetry** (sem Docker)

> Útil para rodar e testar rapidamente em desenvolvimento.

### 1) Criar e ativar ambiente

Na raiz do projeto (onde está o `pyproject.toml`):

```bash
# instala dependências do projeto
poetry install

# ativa o venv
poetry shell
```

> Se preferir venv dentro do diretório do projeto:  
> `poetry config virtualenvs.in-project true`

### 2) Subir banco Postgres local (opções)

- **Via Docker** apenas do Postgres (prático):
  ```bash
  docker run --rm --name pg-local -p 5432:5432     -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=mydatabase     postgres:18
  ```
- **Ou** use um Postgres que você já tenha instalado localmente (ajuste a URL no backend).

### 3) Rodar o **backend** com Poetry

No `backend/database.py`, a URL padrão já aponta para:
```
postgresql+psycopg2://user:password@localhost:5432/mydatabase
```
Se no seu arquivo está usando `@postgres`, mude para `@localhost` quando não estiver no Compose.

Execute:

```bash
# ainda dentro do poetry shell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4) Rodar o **frontend** com Poetry

Em outro terminal (ou outro shell Poetry):

```bash
# se quiser isolar dependências do front no pyproject, adicione as libs:
# poetry add streamlit requests pandas --group frontend
cd frontend
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

Abra http://localhost:8501

---

## Variáveis de ambiente

No **Docker** (já no compose):

- `POSTGRES_DB` = `mydatabase`
- `POSTGRES_USER` = `user`
- `POSTGRES_PASSWORD` = `password`
- `DATABASE_URL` do backend = `postgresql+psycopg2://user:password@postgres:5432/mydatabase`

No **Poetry/local** (sem compose), ajuste a `DATABASE_URL` para `localhost`:

```
postgresql+psycopg2://user:password@localhost:5432/mydatabase
```

> Dica: você pode usar um `.env` e ler com `python-dotenv` ou configurar pela shell antes de rodar o `uvicorn`.

---

## Modelo de dados

**Tabela `products`**:

| Campo            | Tipo     | Observação                 |
|------------------|----------|----------------------------|
| id               | Integer  | PK                         |
| name             | String   |                            |
| description      | String   |                            |
| price            | Float    |                            |
| categoria        | String   |                            |
| email_fornecedor | String   | email                      |
| created_at       | DateTime | `func.now()` no servidor   |

---

## API – Endpoints

Base URL: `http://localhost:8000`

- `GET /products/` → lista todos os produtos
- `GET /products/{product_id}` → retorna um produto
- `POST /products/` → cria produto
- `PUT /products/{product_id}` → atualiza produto (parcial/total)
- `DELETE /products/{product_id}` → remove produto

**Swagger**: http://localhost:8000/docs

---

## Fluxos comuns via cURL

```bash
# Criar
curl -X POST http://localhost:8000/products/   -H "Content-Type: application/json"   -d '{
    "name":"Teclado",
    "description":"Mecânico",
    "price":199.90,
    "categoria":"Eletrônico",
    "email_fornecedor":"fornecedor@exemplo.com"
  }'

# Listar todos
curl http://localhost:8000/products/

# Buscar um
curl http://localhost:8000/products/1

# Atualizar (parcial)
curl -X PUT http://localhost:8000/products/1   -H "Content-Type: application/json"   -d '{"price":179.90}'

# Deletar
curl -X DELETE http://localhost:8000/products/1
```

---

## Dicas de desenvolvimento

- **Pydantic v2**: use `ConfigDict(from_attributes=True)` em respostas ORM (já aplicado).
- **Tratamento no CRUD**: `get_products().all()` (com parênteses); `delete_product` retorna 404 se não achar.
- **Orquestração**:
  - `healthcheck` no Postgres
  - `depends_on` (backend espera Postgres saudável; frontend espera backend)
- **Frontend**:
  - Consome `http://backend:8000/...` quando está no Compose
  - Em dev local, use `http://localhost:8000/...`
  - Adicione `timeout` e `try/except` nos `requests` para mensagens mais amigáveis

---

## Solução de problemas

**1) Postgres não sobe com erro sobre `/var/lib/postgresql/data`**  
A partir do 18, use **`/var/lib/postgresql`**. Zere volume em dev:
```bash
docker compose down -v
docker compose up -d --build
```

**2) Backend erro: `database "mydatabase" does not exist`**  
Se o volume já existia, crie o DB manualmente:
```bash
docker exec -it <container-postgres> psql -U user -c "CREATE DATABASE mydatabase;"
docker compose restart backend
```

**3) Frontend sem conectar no backend (Compose)**  
Espere o backend ficar pronto, atualize a página, e cheque:
```bash
docker compose logs -f backend
```

**4) Poetry/Windows (PowerShell)**  
Se o venv não fica na pasta do projeto:
```powershell
poetry config virtualenvs.in-project true --local
poetry env use python
poetry install
```

---

## Próximos passos (Roadmap)

- Alembic para migrações
- Paginação e filtros no `GET /products/`
- Validações adicionais e testes automatizados (pytest)
- Autenticação (JWT) e autorização
- CORS (se backend for exposto a um front externo ao Compose)
- Observabilidade (logging estruturado / OpenTelemetry)

---

## Licença

Este projeto é disponibilizado sob a licença **MIT**. Sinta-se livre para usar, estudar e contribuir.
