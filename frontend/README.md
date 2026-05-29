# frontend/

React + Vite + TypeScript — **a implementar**. Sem código de app ainda (fase de planejamento).

Design system "Orbital Mission Control" em [`../docs/FRONTEND.md`](../docs/FRONTEND.md). Antes de codar: carregar a skill `whereitfalls-frontend` (e `whereitfalls-context`).

Estrutura planejada:

```
frontend/
├── src/
│   ├── app/            # rotas/páginas
│   ├── components/     # UI (telemetria, painéis, cards)
│   ├── globe/          # globo 3D (react-globe.gl / Cesium) — ilha client-only
│   ├── map/            # mapa de calor (deck.gl / Leaflet)
│   ├── api/            # client tipado gerado do OpenAPI
│   └── styles/         # tokens (paleta, fontes), tailwind
├── index.html
├── package.json
└── Dockerfile
```

Stack: React · Vite · TypeScript · react-globe.gl/three (ou Cesium/Resium) · deck.gl/Leaflet · Motion · Tailwind · Lucide. Fontes: Cabinet Grotesk + Geist + JetBrains Mono (Inter/Roboto/Space Grotesk **proibidos**).
