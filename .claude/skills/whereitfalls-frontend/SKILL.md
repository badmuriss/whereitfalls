---
name: whereitfalls-frontend
description: Regras de frontend do WhereItFalls — design system "Orbital Mission Control" (React+Vite+TS, globo 3D, mapa de calor) com regras anti-AI (derivadas de frontend-design + frontend-outis). Use ao criar/editar qualquer UI, componente, página ou estilo do projeto.
---

# WhereItFalls — Frontend ("Orbital Mission Control")

Dashboard de telemetria espacial. Sala de controle séria (aviação/defesa civil), **não** app de startup genérico. Stack: React + Vite + TypeScript. Detalhe completo em `docs/FRONTEND.md`.

## Direção (commitada — não reinventar a cada tela)

Fundo quase-preto OLED, densidade de cockpit, números em mono, **um** acento de perigo (âmbar). Globo 3D como peça central; painéis de telemetria assimétricos ao redor. Dials: VARIANCE 8 / MOTION 6 / DENSITY 7.

## Tokens

```css
--bg:#06080F; --surface:#0D111C; --surface-2:#131826;
--hairline:rgba(255,255,255,.08); --text:#E6EAF2; --text-dim:#8A93A6;
--accent:#F0A202;       /* hazard amber — único acento */
--accent-hi:#FF6B35;    /* risco crítico, pontual */
--signal:#3DD6C4;       /* dado neutro, parcimônia */ --ok:#4ADE80;
--ease-out:cubic-bezier(.23,1,.32,1);
```

Fontes: **Cabinet Grotesk** (display) + **Geist** (UI) + **JetBrains Mono** (TODOS os números/coords/timers).

## Regras duras (anti-AI — frontend-outis §13)

- **Proibido**: roxo/azul-AI, glow neon, gradiente neon, preto puro.
- **Proibido fontes**: Inter, Roboto, Arial, Space Grotesk. **Serif proibida** (é dashboard).
- Máx 1 acento dominante (âmbar); saturação < 80%.
- Sem 3 cards iguais em linha → grid assimétrico/fracionário. Sem `border-left` callout. Sem pills/círculos decorativos ao redor de títulos.
- Sem números falsos redondos (`99.9%`) → dado real. Sem nomes/avatares genéricos. Sem copy clichê ("Elevate", "Seamless").
- **Sem emoji** em markup/chrome → ícones Lucide (`lucide-react`, stroke-width único). Sem Unsplash.

## Layout & técnica

- `min-h-[100dvh]` (nunca `h-screen`); CSS Grid (nunca `w-[calc()]`). Container `max-w-[1400px] mx-auto`.
- Mobile colapsa p/ coluna única; globo → mapa 2D leve se perf exigir.
- Verificar `package.json` antes de importar lib; gate APIs de browser em boundary client-only.

## Globo 3D & heatmap

- Globo: **react-globe.gl** (rápido) ou Cesium/Resium (preciso) — ilha client-only isolada (three/GSAP só aqui). Camadas: órbita + ground-track + corredor de incerteza + pontos de aeroportos/regiões em âmbar.
- Heatmap: deck.gl/Leaflet, **agregado no backend** (`/v1/risk/heatmap`) — nunca milhares de pontos crus no cliente.

## Motion

`transform`/`opacity` só; UI < 300ms; saída ~75% da entrada; easing `--ease-out`. Reveal de página 1× com stagger 30–80ms. Telemetria que atualiza muito (countdown/coords) **não anima**. `prefers-reduced-motion` respeitado. Hover atrás de `@media (hover:hover) and (pointer:fine)`.

## Estados & a11y (obrigatório)

8 estados (default/hover/focus/active/disabled/loading/error/success). **Skeleton loaders** com forma do layout, nunca spinner. Empty states compostos. `:focus-visible` 2–3px; alvos ≥44px em `pointer:coarse`.

## Type-safety

Cliente da API **gerado do OpenAPI** do backend → tipos e2e. TypeScript estrito.

## Checklist pré-commit

- [ ] Sem AI tells (roxo/neon/Inter/serif/preto puro/cards-3-iguais/border-left/pills decorativos).
- [ ] Fontes do catálogo; números em mono; 1 acento.
- [ ] `min-h-[100dvh]`, grid, mobile colapsa.
- [ ] Estados loading/empty/error; `prefers-reduced-motion`; focus-visible; alvos ≥44px.
- [ ] Globo isolado client-only; heatmap agregado no backend.
