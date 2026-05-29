---
name: whereitfalls-backend
description: Convenções de backend do WhereItFalls (FastAPI Python — ingest de reentrada, órbita com skyfield, risco com shapely/PostGIS, alertas, testes, observabilidade). Use ao criar/editar qualquer código de backend, serviço, modelo, endpoint ou job.
---

# WhereItFalls — Backend (FastAPI / Python)

Pipeline: `ingest` → `orbit` → `risk` → `alerts` + API. Detalhe em `docs/ARCHITECTURE.md` e `docs/DATA_SOURCES.md`.

## Stack & estrutura

FastAPI · APScheduler · skyfield/sgp4 · shapely/geopandas/pyproj · SQLModel · psycopg/PostGIS · httpx · pytest.

```
backend/app/{main.py, core/, models/, schemas/, api/, services/, jobs/}
```

`core/` = config(env)/db/logging/scheduler · `models/` SQLModel · `schemas/` Pydantic · `api/` routers · `services/` ingest|orbit|risk|alerts · `jobs/` tarefas APScheduler.

## Serviços (responsabilidade)

- **ingest.py**: clientes Space-Track (`tip` = reentrada prevista + incerteza + lat/lon; `gp` = TLE), CelesTrak (TLE, sem key), CORDS (histórico). Upsert idempotente. Pulls **espaçados** (respeitar rate limit; cache).
- **orbit.py**: skyfield/sgp4 propaga TLE sobre `[epoch ± incerteza]` → ground-track (lista lat/lon). Sem modelar decaimento — consumir previsão pronta.
- **risk.py**: shapely faz buffer do ground-track → corredor; PostGIS faz overlay com aeroportos/regiões/pop → score por ativo/região.
- **alerts.py**: corredor ∩ assinatura acima do limiar → webhook (httpx POST, assinatura HMAC). Grava `AlertEvent`. (Sem e-mail neste MVP.)

## Convenções

- **Type-safety e2e**: tudo via Pydantic/SQLModel; sem `dict` solto cruzando camada. OpenAPI é o contrato (frontend gera client dele).
- **Geo**: WGS84 / EPSG:4326; GeoJSON na borda; geometria PostGIS no DB.
- **Datas**: UTC, ISO-8601, timezone-aware.
- **Config**: pydantic-settings lendo `.env` (ver `.env.example`). Nunca hardcode segredo.
- **Erros**: exceções → handler → JSON `{error:{code,message}}` + status correto. Validar só na borda (entrada da API / resposta de fonte externa); confiar no código interno.
- **Idempotência**: ingest e recompute devem poder rodar de novo sem duplicar.

## Observabilidade

Logging estruturado (JSON, com norad_id/prediction_id no contexto) · `/health` (DB + última ingestão). Logar falha de fonte externa sem derrubar o job.

## Testes (pytest)

- `orbit`: ground-track de TLE conhecido bate com referência (fixture).
- `risk`: corredor sobre região conhecida gera score esperado; ponto fora → score 0.
- `api`: contrato dos routers (status, schema). Use TestClient.
- Mockar HTTP de fontes externas (não bater na rede em teste).

## Jobs (APScheduler)

`pull_predictions` (a cada `INGEST_INTERVAL_HOURS`) → `recompute_risk` (previsões novas/alteradas). Jobs idempotentes e logados. (Sem job de envio de alerta neste MVP — sem disparo autônomo.)

## Commits

Conventional commits, conciso, sem "Claude Code" na mensagem.
