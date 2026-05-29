# frontend/

React + Vite + TypeScript — dashboard inicial "Orbital Mission Control".

Design system "Orbital Mission Control" em [`../docs/FRONTEND.md`](../docs/FRONTEND.md). Antes de codar: carregar a skill `whereitfalls-frontend` (e `whereitfalls-context`).

Estrutura planejada:

```
frontend/
├── src/
│   ├── api/            # client tipado manual a partir do contrato atual
│   ├── assets/         # logo SVG + conceito raster
│   ├── globe/          # painel orbital visual
│   ├── map/            # heatmap BR esquemático
│   └── styles/         # tokens e layout
├── index.html
├── package.json
└── Dockerfile
```

Stack: React · Vite · TypeScript · react-globe.gl/three (ou Cesium/Resium) · deck.gl/Leaflet · Motion · Tailwind · Lucide. Fontes: Cabinet Grotesk + Geist + JetBrains Mono (Inter/Roboto/Space Grotesk **proibidos**).

## Rodar

```bash
npm install
npm run dev
npm run build
```
