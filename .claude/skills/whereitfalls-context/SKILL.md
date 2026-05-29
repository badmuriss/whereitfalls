---
name: whereitfalls-context
description: Contexto-mestre do projeto WhereItFalls (alerta de queda de detritos espaciais). Carregue SEMPRE primeiro ao trabalhar neste repo — define problema, solução, arquitetura, fontes de dados, glossário e escopo. Use antes de qualquer tarefa de backend, frontend, dados ou docs.
---

# WhereItFalls — Contexto

**Produto:** alerta de queda de detritos espaciais (satélites mortos, estágios de foguete, debris) para defesa civil, aviação e população. Consome previsões de reentrada, calcula o **corredor de risco no solo** e alerta (mapa de calor, webhook).

**Posicionamento (1 frase):** "Eles evitam colisão lá em cima; WhereItFalls avisa quem está embaixo." Apoio à decisão para autoridades — **não** alarme individual.

**Contexto:** projeto FIAP Global Solution "Space Connect". Entrega 2026-06-09. Foco **Brasil-first** (baixa latitude = mais sobrevoos; DECEA; Alcântara).

## Por que existe (validação)

- 1–2 Starlink reentram/dia; quedas reais (Polônia 2025, Quênia, Long March 5B 2022).
- ~10% de chance de vítima por detrito de foguete na década (Byers et al., Nature).
- FAA/UNOOSA/IAA pedem um sistema de aviso — não existe alerta regional grátis/acessível.
- Mercado SSA US$1,7–5 bi; clientes: defesa civil/DECEA/FAB, aviação, **seguradoras** (underwriting), marítimo. COGS ~zero (dado grátis).

## Pipeline (mental model)

`ingest` (Space-Track TIP + CelesTrak + CORDS) → `orbit` (skyfield → ground-track na janela ±incerteza) → `risk` (shapely corredor + PostGIS overlay aeroportos/regiões/pop → score) → `alerts` (webhook) + frontend (globo 3D + heatmap).

## Stack

Python · FastAPI · APScheduler · skyfield/sgp4 · shapely/geopandas · PostgreSQL/PostGIS · SQLModel/Pydantic · React+Vite+TS · react-globe.gl/Cesium · deck.gl/Leaflet · Docker. Deploy: local; produção via Dokploy (dono do repo).

## Glossário

- **Reentrada**: queda de objeto na atmosfera. **TIP**: Tracking and Impact Prediction (Space-Track) — epoch previsto + incerteza(min) + lat/lon.
- **Ground-track**: trilha sub-satélite (projeção da órbita no solo).
- **Corredor de risco**: buffer do ground-track sobre a janela de incerteza.
- **TLE/GP**: elementos orbitais. **SSA**: Space Situational Awareness.
- **FIR**: região de informação de voo (espaço aéreo).

## Escopo / estado

Ver `docs/PLAN.md`. **Estado: planejamento — sem código de app ainda.** MVP = ingest→corredor→overlay→heatmap+API+alerta por webhook. Stretch = heatmap histórico, peso populacional, tier seguro.

## Princípios

Type-safety e2e · observabilidade (logging + /health) · testes (pytest/Vitest) · legibilidade > esperteza · conventional commits (sem "Claude Code" na mensagem).

## Docs de referência

`docs/RESEARCH.md` (pesquisa/negócio) · `docs/ARCHITECTURE.md` · `docs/DATA_SOURCES.md` · `docs/API.md` · `docs/FRONTEND.md` · `docs/PLAN.md`.

## Skills relacionadas

`whereitfalls-backend` (backend) · `whereitfalls-frontend` (frontend).
