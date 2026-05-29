---
name: whereitfalls-context
description: Contexto-mestre do WhereItFalls (alerta de queda de detritos espaciais). Carregue primeiro. Variante Codex — espelha .claude/skills/whereitfalls-context. Ver AGENTS.md.
---

# WhereItFalls — Contexto (Codex)

Variante Codex da skill de contexto. Mantenha em sincronia com `.claude/skills/whereitfalls-context/SKILL.md`.

**Produto:** alerta de queda de detritos espaciais para defesa civil, aviação e população. Consome previsões de reentrada, calcula o **corredor de risco no solo** e alerta (mapa de calor, e-mail, webhook).

**Posicionamento:** "Eles evitam colisão lá em cima; WhereItFalls avisa quem está embaixo." Apoio à decisão — não alarme individual. Projeto FIAP GS "Space Connect", entrega 2026-06-09, **Brasil-first**.

## Por que existe

1–2 Starlink reentram/dia; quedas reais (Polônia 2025, Quênia, Long March 5B 2022). ~10% de chance de vítima por detrito na década (Byers et al., Nature). FAA/UNOOSA/IAA pedem aviso — não há alerta regional grátis. Mercado SSA US$1,7–5 bi; clientes: defesa civil/DECEA/FAB, aviação, **seguradoras**, marítimo. COGS ~zero.

## Pipeline

`ingest` (Space-Track TIP + CelesTrak + CORDS) → `orbit` (skyfield → ground-track ±incerteza) → `risk` (shapely corredor + PostGIS overlay → score) → `alerts` (e-mail/webhook) + frontend (globo 3D + heatmap).

## Stack

Python · FastAPI · APScheduler · skyfield/sgp4 · shapely/geopandas · PostgreSQL/PostGIS · SQLModel/Pydantic · React+Vite+TS · react-globe.gl/Cesium · Docker. Deploy local; produção via Dokploy (dono do repo).

## Glossário

TIP = reentrada prevista (epoch+incerteza+lat/lon) · ground-track = trilha sub-satélite · corredor = buffer do track na janela · TLE/GP = elementos orbitais · SSA = space situational awareness · FIR = região de informação de voo.

## Estado

Planejamento — sem código de app ainda. MVP = ingest→corredor→overlay→heatmap+API+e-mail (ver `docs/PLAN.md`).

## Princípios

Type-safety e2e · observabilidade (logging+Sentry+/health) · testes · legibilidade · conventional commits.

## Docs

`docs/RESEARCH.md` · `ARCHITECTURE.md` · `DATA_SOURCES.md` · `API.md` · `FRONTEND.md` · `PLAN.md`. Skills: `whereitfalls-backend`, `whereitfalls-frontend`.
