---
name: whereitfalls-frontend
description: Frontend do WhereItFalls — design "Orbital Mission Control" (React+Vite+TS, globo 3D, heatmap) + regras anti-AI. Variante Codex — espelha .claude/skills/whereitfalls-frontend. Use ao criar/editar UI.
---

# WhereItFalls — Frontend (Codex)

Variante Codex; manter em sincronia com `.claude/skills/whereitfalls-frontend/SKILL.md`. Detalhe em `docs/FRONTEND.md`.

Dashboard de telemetria espacial — sala de controle séria, não app de startup. React + Vite + TS. Direção commitada: fundo quase-preto OLED, densidade cockpit, números em mono, **um** acento âmbar, globo 3D central. Dials VARIANCE 8 / MOTION 6 / DENSITY 7.

## Tokens

```css
--bg:#06080F; --surface:#0D111C; --surface-2:#131826;
--hairline:rgba(255,255,255,.08); --text:#E6EAF2; --text-dim:#8A93A6;
--accent:#F0A202; --accent-hi:#FF6B35; --signal:#3DD6C4; --ok:#4ADE80;
--ease-out:cubic-bezier(.23,1,.32,1);
```

Fontes: **Cabinet Grotesk** (display) + **Geist** (UI) + **JetBrains Mono** (números/coords/timers).

## Regras duras (anti-AI)

- Proibido: roxo/azul-AI, glow neon, gradiente neon, preto puro.
- Proibido: Inter, Roboto, Arial, Space Grotesk; serif (é dashboard).
- 1 acento dominante; saturação <80%. Sem 3 cards iguais → grid assimétrico. Sem `border-left` callout, sem pills/círculos decorativos.
- Sem números falsos redondos, nomes/avatares genéricos, copy clichê. Sem emoji em chrome → Lucide. Sem Unsplash.

## Layout & técnica

`min-h-[100dvh]` (nunca `h-screen`); CSS Grid (nunca `w-[calc()]`); container `max-w-[1400px]`. Mobile colapsa. Verificar `package.json` antes de importar lib; browser APIs em boundary client-only.

## Globo & heatmap

Globo: react-globe.gl (rápido) ou Cesium/Resium — ilha client-only (three/GSAP isolado). Camadas: órbita + ground-track + corredor + pontos âmbar. Heatmap: deck.gl/Leaflet **agregado no backend** (`/v1/risk/heatmap`).

## Motion / estados / a11y

`transform`/`opacity` só; UI <300ms; reveal 1× stagger 30–80ms; telemetria não anima; `prefers-reduced-motion`. 8 estados; skeleton loaders (sem spinner); `:focus-visible`; alvos ≥44px; hover atrás de `@media (hover:hover) and (pointer:fine)`.

## Type-safety

Client da API gerado do OpenAPI; TypeScript estrito.
