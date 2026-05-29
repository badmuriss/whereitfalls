# Fontes de Dados — WhereItFalls

Todas gratuitas. Verificar acesso/limites no spike do Dia 1.

## 1. Space-Track.org — previsão de reentrada (fonte primária)

- **Conta**: gratuita (cadastro com e-mail). Autentica via login → cookie de sessão na API.
- **API**: `https://www.space-track.org/basicspacedata/query/...` (URLs estáveis e configuráveis).
- **Classe `tip`** (Tracking and Impact Prediction) — o coração do produto:
  - Campos: data/hora prevista de reentrada (UTC), **incerteza em minutos**, **lat/lon** do ponto previsto, nº de órbita, direção de viagem.
  - Exemplo de query: `/basicspacedata/query/class/tip/NORAD_CAT_ID/<id>/orderby/MSG_EPOCH%20DESC`
- **Classe `gp`** — elementos orbitais (TLE/GP) dos objetos ainda em órbita:
  - Decaindo recentemente: `/basicspacedata/query/class/gp/DECAY_DATE/%3Cnow/...` e `decayed/0/EPOCH/%3Enow-30/...`
- **Rate limits**: respeitar limites do Space-Track (não consultar em loop agressivo; agendar pulls espaçados). Ler `EULA`/limites no site.

> A TIP dá o ponto previsto + janela. O corredor de risco vem de propagar o TLE (classe `gp`) sobre [epoch ± incerteza] e dar buffer.

## 2. CelesTrak — TLE/GP (sem chave)

- **Sem key**, formatos TLE/JSON/CSV/XML. `celestrak.org`.
- Uso: TLE atualizado para propagação (fallback/complemento ao Space-Track) e catálogo (SATCAT).
- **Atenção**: transição para catálogo de **6 dígitos** (~jul/2026) — usar formatos novos (JSON/CSV), não TLE cru de 5 dígitos. Pedem checar dados 3–4×/dia (não martelar).

## 3. Aerospace CORDS — histórico + previsões de reentrada

- `aerospace.org/reentries` — banco de reentradas desde 2000 + previsões de objetos de alto interesse.
- Uso: **heatmap histórico** de quedas (narrativa "acontece muito") e validação cruzada das previsões.
- Pode exigir scraping (verificar se há export/CSV). Tratar como fonte secundária.

## 4. Datasets geográficos (seeds em `data/`)

| Dataset | Uso | Licença |
|---------|-----|---------|
| **OurAirports** (CSV) | aeroportos (lat/lon, tipo) para overlay de risco | domínio público |
| **Natural Earth** | fronteiras de países/estados, FIRs | domínio público |
| **IBGE malha municipal** (opcional) | regiões BR detalhadas | aberto |
| **WorldPop / GPW** (opcional, stretch) | densidade populacional p/ peso de risco | aberto (CC BY) |

## 5. E-mail (alertas)

- SMTP genérico ou **SendGrid/Mailgun free tier** para envio transacional. Variável `EMAIL_*` no `.env`.

## Variáveis de ambiente (rascunho `.env.example`)

```
SPACETRACK_USER=
SPACETRACK_PASS=
CELESTRAK_BASE=https://celestrak.org
DATABASE_URL=postgresql+psycopg://wif:wif@db:5432/whereitfalls
SENTRY_DSN=
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USER=
EMAIL_PASS=
EMAIL_FROM=alertas@whereitfalls.app
INGEST_INTERVAL_HOURS=6
```

## Riscos & mitigações

| Risco | Mitigação |
|-------|-----------|
| Acesso/limite Space-Track | spike Dia 1; cache local; pulls espaçados; fallback CelesTrak |
| CORDS sem API limpa | tratar como secundária; scraping leve só p/ histórico |
| Incerteza grande do corredor | posicionar como apoio à decisão (ver RESEARCH §5), mostrar faixa de incerteza explicitamente |
| Catálogo 6 dígitos (jul/2026) | usar formatos JSON/CSV novos desde já |
