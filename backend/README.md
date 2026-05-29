# backend/

FastAPI (Python) — protótipo inicial do pipeline WhereItFalls.

Estrutura planejada (ver [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)):

```
backend/
├── app/              # FastAPI, schemas, serviços orbit/risk/alerts, jobs
├── tests/            # pytest orbit/risk/api
├── pyproject.toml
└── Dockerfile
```

Stack: FastAPI · APScheduler · skyfield/sgp4 · shapely/geopandas/pyproj · SQLModel · psycopg/PostGIS · httpx.

## Rodar

```bash
uv sync --dev
uv run fastapi dev app/main.py
uv run pytest
```

O protótipo usa Space-Track TIP/GP real quando `SPACETRACK_USER` e
`SPACETRACK_PASS` estão configurados. Há cache curto em memória, upsert
idempotente em SQLModel quando `DATABASE_URL` está disponível e fallback demo
para permitir apresentação mesmo se a fonte externa falhar. O próximo passo é
persistir corredores/alert events e trocar o overlay em memória por PostGIS.
