# WhereItFalls

**Alerta de queda de detritos espaciais para defesa civil, aviação e população.**

Sistema que consome previsões de reentrada de objetos espaciais (satélites mortos, estágios de foguete, detritos), calcula o **corredor de risco no solo** e dispara alertas (mapa de calor, webhook) para regiões, aeroportos e órgãos que estão sob a faixa de incerteza.

> Eles evitam colisão lá em cima. **WhereItFalls avisa quem está embaixo.**

Projeto da **Global Solution FIAP — "Space Connect"** (economia espacial). Entrega: **2026-06-09**.

---

## O problema (resumo)

- 1 a 2 satélites Starlink reentram **por dia**; projeção de ~5/dia. Um objeto rastreável reentra a cada ~2,5 dias.
- Quedas reais recentes: Falcon 9 na Polônia (2025), aldeia no Quênia, Long March 5B sobre Indonésia/Malásia (2022).
- Estudo (Byers et al., *Nature Sci. Reports*): ~**10% de chance** de uma vítima humana por detrito de foguete na próxima década; ~26%/ano de detrito cruzar espaço aéreo movimentado.
- FAA, UNOOSA e IAA **pedem** um sistema de aviso para afastar aeronaves/pessoas. **Não existe alerta regional grátis e acessível** — só bancos de dados de especialista.

Detalhes e fontes em [`docs/RESEARCH.md`](docs/RESEARCH.md).

## A solução

Pipeline backend (Python/FastAPI) que:

1. **Ingere** previsões de reentrada (Space-Track TIP + CelesTrak + Aerospace CORDS).
2. **Propaga** a órbita na janela de incerteza (skyfield) → ground-track.
3. **Calcula** o corredor de risco (shapely) e cruza com aeroportos / regiões BR / densidade populacional (PostGIS).
4. **Pontua** o risco por região/ativo.
5. **Alerta**: mapa de calor (frontend React + globo 3D) e webhook para assinantes.

Foco inicial: **Brasil** (baixa latitude = mais sobrevoos de corpos de foguete; DECEA controla espaço aéreo enorme; base de Alcântara).

## Modelo de negócio

API **freemium**: tier público grátis (bem social + adoção) + tiers pagos (SLA, alerta por região, histórico, score de risco, webhook). Clientes: **defesa civil / DECEA / FAB**, **aviação** (companhias, aeroportos), **seguradoras** (aviação + responsabilidade espacial), portos/marítimo. Mercado SSA: US$ 1,7–2,3 bi (2025/26) → 2,8–5 bi (2030–34). COGS ~zero (dado-fonte grátis).

## Status

🟠 **Protótipo em implementação.** O repositório já tem backend FastAPI,
ingest real do Space-Track TIP/GP com cache curto e fallback demo, serviços de
órbita/risco, API `/v1`, frontend React/Vite com dashboard
"Orbital Mission Control", logo inicial e Docker Compose local.

## Estrutura

```
whereitfalls/
├── docs/                 # pesquisa, arquitetura, plano, fontes de dados, API, frontend
├── backend/              # FastAPI + ingest Space-Track + serviços orbit/risk + testes
├── frontend/             # React + Vite + dashboard + assets de marca
├── data/                 # seeds geográficos (regiões BR, aeroportos, fronteiras)
├── .claude/skills/       # skills do projeto — formato Claude Code
└── .codex/skills/        # mesmas skills — formato Codex
```

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [docs/RESEARCH.md](docs/RESEARCH.md) | Pesquisa do tema, concorrentes, caso de negócio + social, fontes |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura do sistema, fluxo de dados, componentes |
| [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) | Space-Track TIP, CelesTrak, CORDS, datasets, auth, rate limits |
| [docs/API.md](docs/API.md) | Design dos endpoints REST, tiers freemium |
| [docs/FRONTEND.md](docs/FRONTEND.md) | Design system espaço/tech + regras anti-AI |
| [docs/PLAN.md](docs/PLAN.md) | Escopo MVP × stretch, roadmap de 15 dias |

## Stack

Python · FastAPI · APScheduler · skyfield/sgp4 · shapely/geopandas · PostgreSQL/PostGIS · React + Vite + TypeScript · react-globe.gl / Cesium · Docker.

## Rodar local

```bash
cp .env.example .env
docker compose up --build
```

Backend: `http://localhost:8002` · Swagger: `http://localhost:8002/docs` · Frontend:
`http://localhost:5173` · PostGIS local: `localhost:55432`.

Credenciais externas:

- Space-Track: crie uma conta gratuita em `https://www.space-track.org/auth/createAccount`
  e preencha `SPACETRACK_USER`/`SPACETRACK_PASS`.
- Assinaturas de alerta (canal webhook) são gratuitas/simuladas neste protótipo
  acadêmico. Não há envio de e-mail neste MVP.

Smoke de integrações:

```bash
curl -X POST http://localhost:8002/v1/ingest/spacetrack/smoke
curl -X POST http://localhost:8002/v1/ingest/spacetrack/sync
```

Com `SPACETRACK_USER` e `SPACETRACK_PASS`, `/v1/reentries`, `/v1/risk` e
`/v1/risk/heatmap` tentam usar TIP/GP reais e gravam previsões no banco quando
`DATABASE_URL` está disponível. Se o banco ou a fonte externa falhar, a API
mantém cache/demo local para não derrubar a apresentação.

Sem Docker:

```bash
cd backend && uv sync --dev && uv run pytest
cd ../frontend && npm install && npm run build
```
