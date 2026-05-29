# WhereItFalls — Claude Code

Alerta de queda de detritos espaciais para defesa civil, aviação e população. Consome previsões de reentrada (Space-Track TIP / CelesTrak / Aerospace CORDS), calcula corredor de risco no solo e alerta (mapa de calor, webhook). Foco Brasil-first. Projeto FIAP GS "Space Connect", entrega 2026-06-09.

## Antes de codar — carregue as skills do projeto

Use as skills em `.claude/skills/`:

- **whereitfalls-context** — SEMPRE primeiro. Problema, solução, arquitetura, fontes de dados, glossário, escopo.
- **whereitfalls-backend** — ao mexer no backend (FastAPI, ingest, skyfield/órbita, shapely/PostGIS, alertas, testes, observabilidade).
- **whereitfalls-frontend** — ao mexer no frontend (React/Vite, globo 3D, mapa de calor, design space/tech, regras anti-AI).

## Princípios (herdados do CLAUDE.md global do Murilo)

- Type-safety e2e (Pydantic/SQLModel no back, TypeScript estrito no front).
- Observabilidade: logging estruturado + `/health`.
- Testes automatizados (pytest no back, Vitest no front).
- Legibilidade/manutenibilidade acima de esperteza.
- Conventional commits, sem "Claude Code" na mensagem.

## Estado atual

Protótipo em implementação. Há backend FastAPI, ingest Space-Track TIP/GP, risco/API,
frontend React/Vite e Docker local.

## Deploy

Local com Docker/docker-compose. Deploy de produção é feito pelo Murilo via **Dokploy** na VPS dele — não configure pipelines externos sem pedir.
