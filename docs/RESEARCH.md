# Pesquisa & Caso de Negócio — WhereItFalls

## 1. O problema é real e está crescendo

| Fato | Número | Fonte |
|------|--------|-------|
| Reentradas de Starlink | 1–2 por dia hoje; projeção ~5/dia | EarthSky |
| Objeto rastreável reentrando | 1 a cada ~2,5 dias; detrito a cada ~26,5 h | Aerospace / CORDS |
| Risco de vítima humana (década) | ~10% por detrito de foguete | Byers et al., *Nature Scientific Reports* (2024) |
| Detrito em espaço aéreo movimentado | ~26%/ano | estudo de fechamento de espaço aéreo (2024) |
| Alvo de risco de reentrada descontrolada (SpaceX) | 1 em 10.000 por estrutura | doc SpaceX "targeted reentry" |

**Quedas reais recentes:** estágio de Falcon 9 na **Polônia** (fev/2025); fragmentos em aldeia no **Quênia**; Long March 5B sobre **Indonésia/Malásia** (2022); detritos da Blue Origin. (BBC, Wikipedia "List of space debris fall incidents").

Causa estrutural: megaconstelações (Starlink, Kuiper) deorbitando ao fim da vida útil → volume de reentradas só sobe.

## 2. Por que é bom para a sociedade

- **Segurança da aviação**: já houve **fechamento de espaço aéreo** por reentrada (Espanha/França, nov/2022). Fechar espaço aéreo custa caro mesmo sem impacto. *Nature Sci. Reports (2024)* documenta o risco a aeronaves.
- **Demanda institucional não atendida**: FAA (relatório ao Congresso), UNOOSA e IAA **pedem explicitamente** um sistema de aviso para afastar aeronaves/pessoas de detritos caindo. Hoje só há bancos de dados de especialista (Aerospace CORDS) — **nenhum alerta regional grátis e acessível**.
- **Equidade / Brasil**: corpos de foguete sobrevoam mais as **baixas latitudes** → Sul Global carrega risco desproporcional. Brasil = território enorme, baixa latitude, DECEA controla espaço aéreo gigante (incl. oceânico), base de Alcântara. Relevância nacional direta e desatendida.
- **Tier público grátis** democratiza um aviso hoje trancado em silos de defesa/especialista.

## 3. Por que é vendável

- **Mercado SSA** (Space Situational Awareness): US$ 1,7–2,3 bi em 2025/26 → US$ 2,8–5 bi em 2030–2034, CAGR ~7–10% (MarketsandMarkets, Fortune Business Insights, Mordor).
- **Compradores existem**: US Office of Space Commerce contratou SSA comercial (LeoLabs, Slingshot, COMSPOC); UK Space Agency idem.
- **Seguros** (segmento que o Murilo quer priorizar): existe **mercado de seguro de responsabilidade por detritos espaciais** (Dataintelo). Dado de risco de reentrada alimenta **subscrição/precificação** de apólices de aviação e responsabilidade espacial. Caso de uso premium: API de score de risco + histórico para underwriting.
- **COGS ~zero**: dado-fonte é grátis (Space-Track TIP, CelesTrak, CORDS) → margem alta.

### Segmentos de cliente

| Segmento | Uso | Tier |
|----------|-----|------|
| Defesa civil / DECEA / FAB | gerenciar espaço aéreo e resposta no solo | B2G (pago) |
| Companhias aéreas / aeroportos | desvio de rota, awareness operacional | B2B (pago) |
| **Seguradoras (aviação + responsabilidade espacial)** | **score de risco + histórico p/ underwriting** | **B2B premium** |
| Portos / marítimo | risco sobre rotas e zonas de exclusão | B2B (pago) |
| Público / pesquisadores / imprensa | awareness, transparência | grátis |

## 4. Concorrência e a brecha

| Player | O que faz | Limite |
|--------|-----------|--------|
| LeoLabs / Slingshot / COMSPOC | SSA enterprise, colisão **em órbita** | caro, defesa/operador, não foca risco no solo |
| SpaceX Stargaze | SSA via sensores Starlink, colisão em órbita | B2B, fechado, "para cima" |
| Aerospace CORDS | banco de reentradas + previsões | voltado a especialista, não é alerta regional |
| Orbital Radar (consumer) | tracker de reentrada + alerta de proximidade individual | gadget de proximidade pessoal, não B2B/aviação/regional |
| Aviosonic | hardware embarcado no próprio detrito | hardware, não plataforma de dados |

**Brecha do WhereItFalls:** plataforma de software que traduz previsão de reentrada em **risco regional acionável** (aviação, defesa civil, seguro), com mapa de calor + API + alertas, **acessível e Brasil-first**. Ninguém ocupa esse vão de graça/acessível.

## 5. O contra honesto (e o reenquadramento)

A previsão de reentrada tem **~±20% de incerteza** na janela orbital → a pegada no solo é enorme e a probabilidade individual é baixa. Crítica esperada: "alarmismo".

**Reenquadramento (defensável):** o produto **não** promete "vai cair em você". É **apoio à decisão** — qual aeroporto / corredor aéreo / região está sob a faixa de incerteza, para a autoridade gerenciar espaço aéreo (que **já fecha hoje**) e priorizar resposta. É sistêmico e operacional, não pânico. Esse é exatamente o vão apontado pela literatura (FAA/UNOOSA/IAA).

## 6. Ideias de diferencial (para o pitch / roadmap)

- **Globo 3D** (Cesium/react-globe.gl) mostrando órbita do objeto + ground-track + corredor de incerteza animado. O "uau" visual.
- **Mapa de calor** de risco por região + heatmap **histórico** de quedas (CORDS) → narrativa "isto acontece muito".
- **Countdown** para a janela de reentrada + nível de confiança.
- **Score de risco** por ativo (aeroporto, cidade) e por apólice (seguro).
- **Alertas** por **webhook** B2B por região assinada (integra com despacho/sistemas de defesa civil).

## Fontes

- EarthSky — reentradas diárias de Starlink.
- Aerospace Corporation / CORDS — `aerospace.org/reentries`.
- Byers et al., *Nature Scientific Reports* (2024) — "Airspace closures due to reentering space objects".
- *Acta Astronautica* — "Uncontrolled reentries of space objects and aviation safety".
- FAA — "Risks Associated with Reentry Disposal of Satellites" (relatório ao Congresso).
- UNOOSA / IAA — papers sobre alerta de reentrada para aviação (R-DBAS).
- BBC / Wikipedia — incidentes de queda (Polônia, Quênia, Long March 5B).
- MarketsandMarkets / Fortune Business Insights / Mordor Intelligence — mercado SSA.
- Dataintelo — mercado de seguro de responsabilidade por detritos.
- Convergência Digital (23/02/2026) — SpaceX Stargaze.
