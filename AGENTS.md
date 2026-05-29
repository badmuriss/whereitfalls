# WhereItFalls — Codex / Agents

Alerta de queda de detritos espaciais para defesa civil, aviação e população. Consome previsões de reentrada (Space-Track TIP / CelesTrak / Aerospace CORDS), calcula corredor de risco no solo e alerta (mapa de calor, e-mail, webhook). Foco Brasil-first. Projeto FIAP GS "Space Connect", entrega 2026-06-09.

## Skills do projeto (formato Codex)

Carregue as skills em `.codex/skills/` antes de trabalhar:

- **whereitfalls-context** — sempre primeiro. Problema, solução, arquitetura, fontes de dados, glossário, escopo.
- **whereitfalls-backend** — backend Python/FastAPI: ingest, órbita (skyfield), risco (shapely/PostGIS), alertas, testes.
- **whereitfalls-frontend** — frontend React/Vite: globo 3D, mapa de calor, design space/tech, regras anti-AI.

As mesmas skills existem em `.claude/skills/` para Claude Code — mantenha as duas versões em sincronia ao editar conteúdo.

## Princípios

- Type-safety e2e (Pydantic/SQLModel; TypeScript estrito).
- Observabilidade (logging estruturado, `/health`).
- Testes (pytest; Vitest).
- Legibilidade > esperteza. Conventional commits.

## Estado

Protótipo em implementação — backend FastAPI, ingest Space-Track TIP/GP, risco/API,
frontend React/Vite e Docker local.

## Deploy

Local via Docker. Produção: Dokploy na VPS (responsabilidade do dono do repo).
