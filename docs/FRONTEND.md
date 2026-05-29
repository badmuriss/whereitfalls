# Frontend — Design System "Orbital Mission Control"

Regras derivadas das skills `frontend-design` (Anthropic) e `frontend-outis` (repo vizinho), adaptadas a um dashboard de telemetria espacial. Stack: **React + Vite + TypeScript**, globo 3D, mapa de calor. A skill do projeto `whereitfalls-frontend` resume isto para uso em código.

## Direção estética (commitada)

**Orbital Mission Control / Telemetria.** Sala de controle: fundo quase-preto OLED, densidade de cockpit, números em monoespaçada, um único acento de **perigo** (âmbar/laranja) para risco. Sensação: instrumento sério de aviação/defesa civil — **não** "app de startup genérico". Tier (frontend-outis): **Tech/SaaS full-premium** porém **dashboard** (densidade alta, serif proibida).

Dials: `DESIGN_VARIANCE 8` · `MOTION_INTENSITY 6` · `VISUAL_DENSITY 7 (cockpit)`.

## Paleta

```css
--bg:        #06080F;  /* near-black OLED, NUNCA preto puro */
--surface:   #0D111C;  /* cards/superfícies */
--surface-2: #131826;
--hairline:  rgba(255,255,255,0.08);
--text:      #E6EAF2;
--text-dim:  #8A93A6;
--accent:    #F0A202;  /* HAZARD AMBER — único acento, risco/alerta */
--accent-hi: #FF6B35;  /* laranja para risco crítico (uso pontual) */
--signal:    #3DD6C4;  /* teal/cyan dessaturado p/ dado neutro (parcimônia) */
--ok:        #4ADE80;  /* status nominal */
```

Regras de cor (de frontend-outis):
- **Máx 1 acento dominante** (âmbar). Cyan é secundário e parcimonioso.
- **THE LILA BAN**: roxo/azul-AI **proibido**. Sem glows neon, sem gradientes neon.
- **Sem preto puro** — usar `#06080F`.
- Saturação dos acentos < 80%.

## Tipografia

| Papel | Fonte | Notas |
|------|-------|-------|
| Display/headers | **Cabinet Grotesk** (ou Clash Display) | técnico, característico; `tracking-tighter` |
| Body/UI | **Geist** | limpo, moderno |
| Telemetria/números | **JetBrains Mono** (ou Geist Mono) | TODOS os números, coordenadas, timers em mono |

Bans: **Inter, Roboto, Arial, Space Grotesk proibidos.** Serif **proibida** (é dashboard, não editorial). `font-display: swap`. Máx 2 famílias + a mono.

## Layout

- Cockpit: `VISUAL_DENSITY 7` → paddings menores, divisores 1px (`--hairline`), dados compactos.
- **Globo 3D** como herói central (não um hero de marketing). Painéis de telemetria ao redor (assimétrico, grid fracionário — não 3 colunas Bootstrap).
- `min-h-[100dvh]`, nunca `h-screen`. Grid CSS, nunca `w-[calc()]`.
- Mobile: colapsa para coluna única; globo vira mapa 2D leve se perf exigir.

## O globo 3D (peça central)

- **react-globe.gl** (three.js, mais simples) ou **CesiumJS/Resium** (preciso, "aerospace"). Decidir no spike — começar com react-globe.gl pela velocidade.
- Camadas: Terra escura + arco da **órbita** do objeto, **ground-track** previsto, **corredor de incerteza** (faixa), pontos de **aeroportos/regiões** sob risco pulsando em âmbar.
- Isolado em boundary client-only (não interfere em hidratação). GSAP/three só nessa ilha.

## Mapa de calor

- Heatmap de risco (intensidade = score × população/tráfego) sobre Brasil; heatmap histórico de quedas (CORDS) em aba separada.
- Render via deck.gl/Leaflet.heat — performance: agregação no backend (`/v1/risk/heatmap`), não milhares de pontos crus no cliente.

## Motion (frontend-outis)

- `transform`/`opacity` só. Easing custom (`--ease-out: cubic-bezier(0.23,1,0.32,1)`). UI < 300ms; saída ~75% da entrada.
- Reveal de página orquestrado uma vez (stagger 30–80ms). Nada de micro-animação espalhada.
- **Nunca** animar ação de teclado. `prefers-reduced-motion` respeitado (mantém opacity, remove movimento).
- Telemetria que atualiza muito (countdown, coords) **não anima** — só troca número.

## AI Tells a EVITAR (de frontend-outis §13)

- Sem glow neon / gradiente neon / roxo-AI.
- Sem preto puro; sem fontes genéricas (Inter etc.).
- Sem 3 cards iguais em linha (usar grid assimétrico/zig-zag).
- Sem `border-left: Npx solid` callout (cliché de dashboard AI).
- Sem pills decorativos flutuando ao redor do título; sem círculo/anel decorativo atrás do header.
- Sem números falsos redondos (`99.9%`, `50%`) — usar dado real/orgânico.
- Sem nomes/avatares genéricos; sem clichês de copy ("Elevate", "Seamless", "Next-Gen").
- Sem emojis em markup/chrome — usar ícones (Lucide `lucide-react`, stroke-width único).
- Sem Unsplash — usar asset próprio/placeholder.

## Estados & a11y (obrigatórios)

- 8 estados por componente: default/hover/focus/active/disabled/loading/error/success.
- **Skeleton loaders** com forma do layout — nunca spinner genérico.
- Empty states compostos; erros inline e claros.
- `:focus-visible` (2–3px, contraste 3:1); alvos ≥ 44px em `pointer: coarse`.
- Hover atrás de `@media (hover:hover) and (pointer:fine)`.

## Performance

- Grain/noise só em `fixed inset-0 z-50 pointer-events-none`. `backdrop-blur` só em fixed/sticky.
- Acelerar só `transform`/`opacity`. Globo three.js em ilha isolada e memoizada.
- Cliente tipado gerado do OpenAPI do backend (type-safety e2e).
