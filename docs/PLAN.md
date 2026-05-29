# Plano de Execução — WhereItFalls

Mini-challenge de 15 dias (FIAP GS). Entrega **2026-06-09**. Princípio: entregar **produto completo mas enxuto** — MVP fechado é melhor que stretch pela metade.

## Escopo

### MVP (obrigatório)
- Ingest de previsões: Space-Track `tip` + CelesTrak TLE (CORDS opcional).
- Propagação → ground-track na janela de incerteza (skyfield).
- Corredor de risco (shapely) + overlay com aeroportos + regiões BR (PostGIS) → score.
- API REST: `/v1/reentries`, `/v1/risk`, `/v1/risk/heatmap`, `/health` + Swagger.
- Frontend: globo 3D (órbita + corredor) + lista de reentradas + mapa de calor de risco.
- Alerta por **e-mail** em região assinada.
- Docker Compose (backend + PostGIS + frontend) rodando local.
- README + testes essenciais (orbit/risk) + observabilidade (logging + `/health`).

### Stretch (se sobrar tempo)
- **Webhooks** B2B + assinatura HMAC.
- Heatmap **histórico** de quedas (CORDS).
- Peso por **densidade populacional** (WorldPop).
- Tier **Insurance**: score por ativo/apólice + analytics histórico.
- API keys / tiers freemium.
- Corredor de voo (rotas aéreas) no overlay.

## Roadmap (15 dias)

| Dias | Entrega | Notas |
|------|---------|-------|
| 1–2 | Repo, FastAPI skeleton, models/migrations, **spike Space-Track/CelesTrak** | validar acesso TIP + parsing |
| 3–5 | `orbit` (ground-track) + `risk` (corredor + overlay aeroportos/regiões + score) | núcleo técnico |
| 6–8 | Endpoints API + frontend: globo 3D + mapa de calor | "uau" visual |
| 9–10 | E-mail + assinaturas; (webhooks se der) | alertas |
| 11–12 | Polish UI (design system "Mission Control"), heatmap histórico, README | anti-AI |
| 13 | Testes, observabilidade, dockerizar tudo | qualidade |
| 14 | Gravar demo (4 min) + vídeo-pitch | entrega |
| 15 | Buffer / margem | imprevistos |

## Entregáveis FIAP

- **Repositório GitHub** (público/privado c/ tutor) — README com descrição, tecnologias, instruções de execução. ✅ coberto.
- **Vídeo até 4 min** (parte 2 — nota GS1): problema, solução, tecnologias, **demo do protótipo rodando**, resultados/impacto.
- **Vídeo-pitch até 3 min** (parte 1 — prêmio): solução fictícia convincente (pode focar a visão completa + mercado).
- `.txt` com links + `.txt` com RMs e nomes; tudo em `.zip` na plataforma ON.

## Riscos

| Risco | Mitigação |
|------|-----------|
| Acesso/limite Space-Track | spike Dia 1, cache, fallback CelesTrak |
| Cálculo do corredor de incerteza | consumir ponto TIP + buffer do ground-track; não modelar decaimento |
| Globo 3D consumir tempo | começar react-globe.gl (rápido); Cesium só se sobrar |
| Escopo inflar | travar MVP; stretch só depois de MVP fechado |

## Definição de pronto (MVP)

- [ ] `docker compose up` sobe backend + DB + frontend local.
- [x] Ingest popula reentradas reais do Space-Track.
- [x] `/v1/reentries` e `/v1/risk` retornam dados coerentes.
- [x] Upsert idempotente de objetos/previsões em SQLModel quando DB está disponível.
- [x] Recompute persiste corredores de risco gerados em SQLModel.
- [ ] Globo mostra órbita + corredor; heatmap mostra risco sobre BR.
- [ ] Assinar região e receber e-mail de alerta funciona (simulado/free no MVP acadêmico).
- [x] Testes de orbit/risk passam; `/health` ok.
- [ ] README permite rodar do zero.
