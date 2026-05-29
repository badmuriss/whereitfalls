# Arquitetura — WhereItFalls

## Visão geral

Monorepo com backend Python (FastAPI) + frontend React, banco PostgreSQL/PostGIS, orquestrado por Docker Compose para rodar local. Deploy de produção via Dokploy (VPS) é feito depois pelo dono do repo.

```
┌──────────────┐   pull periódico   ┌─────────────────────────────────────┐
│ Space-Track  │ ─────────────────► │ ingest.py                            │
│ TIP / GP     │                    │  - TIP: reentrada prevista + janela  │
│ CelesTrak    │                    │  - TLE: elementos orbitais           │
│ Aerospace    │                    │  - CORDS: histórico (heatmap)        │
│ CORDS        │                    └──────────────┬──────────────────────┘
└──────────────┘                                   │ objetos + previsões
                                                    ▼
                              ┌──────────────────────────────────────┐
                              │ orbit.py (skyfield/sgp4)             │
                              │  propaga TLE na janela ±incerteza   │
                              │  → ground-track (lista lat/lon)     │
                              └──────────────┬──────────────────────┘
                                             ▼
                              ┌──────────────────────────────────────┐
                              │ risk.py (shapely + PostGIS)         │
                              │  corredor = buffer do ground-track  │
                              │  ∩ aeroportos / regiões BR / pop    │
                              │  → score de risco por ativo/região  │
                              └──────────────┬──────────────────────┘
                                             ▼
        ┌────────────────────────────────────────────────────────────┐
        │ PostgreSQL + PostGIS  (objetos, previsões, corredores,       │
        │  regiões, assinaturas, alertas, webhooks)                    │
        └───────────┬───────────────────────────────────┬─────────────┘
                    ▼                                     ▼
        ┌────────────────────┐                ┌────────────────────────┐
        │ FastAPI (REST)     │                │ alerts.py              │
        │ /reentries /risk   │                │  webhook (httpx POST)  │
        │ /subscriptions     │                │  payload assinado HMAC │
        │ /health  + Swagger │                │  corredor ∩ assinatura │
        └─────────┬──────────┘                │  ∩ região assinada     │
                  │ JSON                        └────────────────────────┘
                  ▼
        ┌────────────────────────────────────────────┐
        │ Frontend React + Vite + TS                  │
        │  globo 3D (órbita + corredor) + mapa calor  │
        │  lista de reentradas + countdown + score    │
        └────────────────────────────────────────────┘
```

## Componentes do backend (`backend/app/`)

| Módulo | Responsabilidade |
|--------|------------------|
| `core/` | config (env), conexão DB, logging estruturado, scheduler |
| `models/` | SQLModel: `SpaceObject`, `ReentryPrediction`, `RiskCorridor`, `Region`, `Asset`, `Subscription`, `WebhookEndpoint`, `AlertEvent` |
| `schemas/` | Pydantic — contratos de entrada/saída da API (type-safe) |
| `api/` | routers: `reentries`, `risk`, `subscribe`, `webhooks`, `health` |
| `services/ingest.py` | cliente Space-Track (TIP/GP); CelesTrak/CORDS entram como próximos incrementos |
| `services/repository.py` | upsert idempotente SQLModel de objetos/previsões; fallback seguro quando DB indisponível |
| `services/orbit.py` | skyfield/sgp4 → ground-track na janela de incerteza |
| `services/risk.py` | shapely (buffer/corredor) + PostGIS (overlay, score) |
| `services/alerts.py` | webhook assinado (HMAC) para assinatura cujo corredor cruza a região |
| `jobs/` | tarefas APScheduler: `pull_predictions`, `recompute_risk` |

## Modelo de dados (núcleo, rascunho)

- **SpaceObject**: norad_id, nome, tipo (payload/rocket_body/debris), país, massa estimada.
- **ReentryPrediction**: object_id, fonte (tip/cords), epoch previsto (UTC), incerteza (min), lat/lon previstos, nº órbita, atualizado_em.
- **RiskCorridor**: prediction_id, geometria (LINESTRING/POLYGON, PostGIS), gerado_em.
- **Region**: nome, tipo (estado/município/FIR), geometria (POLYGON), população.
- **Asset**: nome, tipo (aeroporto/porto/cidade), ponto (POINT), peso de exposição.
- **Subscription**: canal (webhook), alvo (region_id/bbox), limiar de risco.
- **AlertEvent**: prediction_id, subscription_id, score, enviado_em, status.

## Fluxo de execução

1. `pull_predictions` (scheduler, a cada N h) → `ingest` busca TIP/GP/CORDS → upsert.
2. Para cada previsão nova/atualizada → `orbit` gera ground-track → `risk` gera corredor + score por região/ativo (PostGIS).
3. Assinaturas (canal webhook) registram região + limiar; quando um corredor cruza a região acima do limiar, `alerts` envia webhook assinado e grava `AlertEvent`.
4. Frontend consome `/reentries` e `/risk` para globo 3D + heatmap; assinaturas via `/subscriptions`.

## Decisões técnicas

- **Consumir previsão pronta** (TIP/CORDS) em vez de modelar decaimento orbital → de-risca o cálculo pesado.
- **PostGIS** para overlay espacial (corredor ∩ ativos) em vez de geometria em memória → escala e simplifica consultas.
- **Statistical/derivado, não imagem** → sem processamento de raster pesado no MVP (densidade populacional é opcional/stretch).
- **FastAPI** → Swagger automático reforça a narrativa "produto = API" e facilita a demo.

## Observabilidade & qualidade

- Logging estruturado (JSON) + endpoint `/health`.
- Testes: pytest (unit dos serviços orbit/risk com fixtures de TLE/previsão conhecidos; contrato dos routers).
- Type-safety: Pydantic/SQLModel no backend; TypeScript estrito no frontend; OpenAPI gerado → client tipado no front.
