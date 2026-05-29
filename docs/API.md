# API — WhereItFalls

REST com FastAPI. OpenAPI/Swagger automático em `/docs`. JSON em tudo. Versionada sob `/v1`.

## Endpoints (rascunho)

### Público (tier grátis)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/v1/reentries` | Lista reentradas previstas (próximas N). Query: `from`, `to`, `min_confidence`, `limit`. |
| GET | `/v1/reentries/{norad_id}` | Detalhe de um objeto + previsão + janela + ground-track. |
| GET | `/v1/risk` | Risco por região. Query: `region` (UF/FIR), `bbox`, `min_score`. |
| GET | `/v1/risk/heatmap` | GeoJSON / pontos ponderados para o mapa de calor. |
| GET | `/v1/history` | Reentradas históricas (CORDS) para heatmap histórico. |
| GET | `/health` | Liveness/readiness. |

### Autenticado (tiers pagos — API key)

| Método | Rota | Tier | Descrição |
|--------|------|------|-----------|
| POST | `/v1/subscriptions` | Pago | Cria assinatura de alerta (canal, alvo, limiar). |
| GET/DELETE | `/v1/subscriptions/{id}` | Pago | Gerencia assinatura. |
| POST | `/v1/webhooks` | Pago | Registra endpoint webhook (URL, secret). |
| GET | `/v1/risk/score` | Premium (seguro) | Score detalhado por ativo/apólice + incerteza. |
| GET | `/v1/history/analytics` | Premium (seguro) | Estatísticas históricas p/ underwriting. |

## Contratos (exemplos)

`GET /v1/reentries` →
```json
{
  "items": [
    {
      "norad_id": 12345,
      "name": "CZ-5B R/B",
      "type": "rocket_body",
      "country": "PRC",
      "predicted_reentry_utc": "2026-06-02T14:35:00Z",
      "uncertainty_minutes": 120,
      "predicted_lat": -12.7,
      "predicted_lon": -45.2,
      "confidence": "medium",
      "max_region_score": 0.78
    }
  ],
  "total": 1
}
```

`POST /v1/subscriptions` ←
```json
{
  "channel": "webhook",
  "target": { "type": "region", "region": "FIR-Brasília" },
  "min_score": 0.5,
  "webhook_id": "wh_abc"
}
```

Webhook payload (POST do WhereItFalls → assinante), assinado com HMAC:
```json
{
  "event": "risk_alert",
  "prediction_id": "...",
  "norad_id": 12345,
  "region": "FIR-Brasília",
  "score": 0.78,
  "window_utc": ["2026-06-02T13:35:00Z", "2026-06-02T15:35:00Z"],
  "corridor_geojson": { "...": "..." }
}
```

## Tiers (freemium)

| Tier | Inclui | Público |
|------|--------|---------|
| **Free** | leitura de reentradas, risco por região, heatmap, histórico | público, pesquisa, imprensa |
| **Pro** | assinaturas de alerta (e-mail/webhook), SLA, rate maior | aviação, aeroportos, defesa civil |
| **Insurance** | score por ativo/apólice, analytics histórico, incerteza detalhada, export | seguradoras (underwriting) |

## Convenções

- Erros: JSON `{ "error": { "code", "message" } }`, status HTTP correto.
- Paginação por `limit`/`offset` ou cursor.
- Rate limit por API key (tier).
- Datas sempre UTC ISO-8601.
- Geo sempre GeoJSON (WGS84 / EPSG:4326).
- Autenticação por API key (header `X-API-Key`) — auth simples no MVP; OAuth fica para depois.
