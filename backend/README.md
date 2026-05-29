# backend/

FastAPI (Python) — **a implementar**. Sem código de app ainda (fase de planejamento).

Estrutura planejada (ver [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)):

```
backend/
├── app/
│   ├── main.py
│   ├── core/         # config, db, logging, sentry, scheduler
│   ├── models/       # SQLModel
│   ├── schemas/      # Pydantic
│   ├── api/          # routers: reentries, risk, subscribe, webhooks, health
│   ├── services/     # ingest, orbit, risk, alerts
│   └── jobs/         # tarefas APScheduler
├── tests/            # pytest
├── pyproject.toml
└── Dockerfile
```

Stack: FastAPI · APScheduler · skyfield/sgp4 · shapely/geopandas/pyproj · SQLModel · psycopg/PostGIS · httpx · sentry-sdk.

Antes de codar: carregar a skill `whereitfalls-backend` (e `whereitfalls-context`).
