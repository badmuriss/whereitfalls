# data/

Seeds geográficos para overlay de risco — **a baixar na implementação** (não versionar arquivos grandes; ver `.gitignore`).

| Arquivo/fonte | Uso | Licença |
|---------------|-----|---------|
| OurAirports (`airports.csv`) | aeroportos (lat/lon, tipo) | domínio público |
| Natural Earth (`ne_*_admin`) | fronteiras países/estados/FIR | domínio público |
| IBGE malha municipal (opcional) | regiões BR detalhadas | aberto |
| WorldPop/GPW (opcional, stretch) | densidade populacional (peso de risco) | CC BY |

Scripts de carga (seed → PostGIS) ficarão em `backend/app/jobs/` ou `data/scripts/`. Detalhes em [`../docs/DATA_SOURCES.md`](../docs/DATA_SOURCES.md).
