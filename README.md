# Desafio Técnico - Pipeline ETL de Produtos

Pipeline de dados ETL desenvolvido em Python que extrai produtos da API FakeStore, transforma os dados com PySpark e carrega em banco PostgreSQL.

## 📋 Visão Geral

Este projeto implementa um pipeline ETL (Extract, Transform, Load) completo:

1. **Extract**: Busca produtos da [FakeStore API](https://fakestoreapi.com/docs)
2. **Transform**: Processa com PySpark - filtra e sumariza por categoria
3. **Load**: Persiste no PostgreSQL com controle transacional

### Fluxo de Dados

```
FakeStore API → Extração → DataFrame Spark → Filtros → Sumarização → Batches → PostgreSQL
                                    ↓
                          - price >= 100.0
                          - rating >= 3.5
```

## 🚀 Como Executar

### Pré-requisitos

- Docker e Docker Compose

### Executar Pipeline Completo

```bash
# Subir PostgreSQL + Executar migrations + Pipeline
docker compose up --build
```

### Parar containers

```bash
docker compose down -v
```

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| API_BASE_URL | URL da FakeStore API | https://fakestoreapi.com |
| API_TIMEOUT | Timeout em segundos | 30 |
| API_RETRY_ATTEMPTS | Tentativas de retry | 3 |
| DB_HOST | Host do PostgreSQL | postgres |
| DB_PORT | Porta do PostgreSQL | 5432 |
| DB_NAME | Nome do banco | fke_database |
| DB_USER | Usuário | fke_user |
| DB_PASSWORD | Senha | fke_password |
| PIPELINE_MIN_PRICE | Preço mínimo filtro | 100.0 |
| PIPELINE_MIN_RATING | Avaliação mínima filtro | 3.5 |
| PIPELINE_BATCH_SIZE | Tamanho do lote | 5 |

---
