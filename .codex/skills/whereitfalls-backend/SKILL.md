---
name: whereitfalls-backend
description: Backend do WhereItFalls (FastAPI Python — ingest reentrada, órbita skyfield, risco shapely/PostGIS, alertas, testes). Variante Codex — espelha .claude/skills/whereitfalls-backend. Use ao editar backend.
---

# WhereItFalls — Backend (Codex)

Variante Codex; manter em sincronia com `.claude/skills/whereitfalls-backend/SKILL.md`. Detalhe em `docs/ARCHITECTURE.md` e `docs/DATA_SOURCES.md`.

Pipeline: `ingest` → `orbit` → `risk` → `alerts` + API.

## Stack & estrutura

FastAPI · APScheduler · skyfield/sgp4 · shapely/geopandas/pyproj · SQLModel · psycopg/PostGIS · httpx · pytest.
`backend/app/{main.py, core/, models/, schemas/, api/, services/, jobs/}`.

## Serviços

- **ingest.py**: Space-Track `tip` (reentrada + incerteza + lat/lon) e `gp` (TLE); CelesTrak (TLE, sem key); CORDS (histórico). Upsert idempotente, pulls espaçados (rate limit + cache).
- **orbit.py**: skyfield propaga TLE em `[epoch ± incerteza]` → ground-track. Consumir previsão pronta, não modelar decaimento.
- **risk.py**: shapely buffer → corredor; PostGIS overlay aeroportos/regiões/pop → score.
- **alerts.py**: corredor ∩ assinatura > limiar → webhook (HMAC). Grava `AlertEvent`. (Sem e-mail neste MVP.)

## Convenções

- Type-safety e2e (Pydantic/SQLModel; sem dict solto). OpenAPI = contrato.
- Geo WGS84/EPSG:4326; GeoJSON na borda; PostGIS no DB. Datas UTC ISO-8601.
- Config via pydantic-settings + `.env` (`.env.example`); sem segredo hardcoded.
- Erros → handler → JSON `{error:{code,message}}`. Validar só na borda. Ingest/recompute idempotentes.

## Observabilidade & testes

Logging estruturado (norad_id/prediction_id no contexto) · `/health`. Falha de fonte externa loga sem derrubar job.
pytest: orbit (ground-track de TLE conhecido), risk (score esperado/ponto fora=0), api (contrato via TestClient), mockar HTTP externo.

## Jobs

APScheduler: `pull_predictions` → `recompute_risk`. Idempotentes e logados. (Sem job de envio de alerta neste MVP.)

Commits: conventional, sem "Claude Code".
