# WhereItFalls — Documento de Pitch

**FIAP Global Solution · Space Connect — economia espacial.** Vídeo-pitch (parte 1, ~3 min). Companion escrito do deck `slides-pitch.html`.

> **Eles evitam colisão lá em cima. WhereItFalls avisa quem está embaixo.**

---

## 1. Resumo executivo

WhereItFalls é uma plataforma que transforma previsões de reentrada de objetos espaciais (satélites mortos, estágios de foguete, detritos) em **alerta de risco no solo**, acionável para **defesa civil, aviação e seguradoras**. Consome dado orbital gratuito, calcula o **corredor de risco** sobre o território e dispara alertas (mapa de calor, e-mail, webhook). Foco inicial: **Brasil**.

## 2. O problema

O céu de órbita baixa está congestionando, e o que sobe está descendo cada vez mais:

- **1 a 2 satélites Starlink reentram por dia** (projeção ~5/dia); um objeto rastreável a cada ~2,5 dias.
- Quedas reais recentes: estágio de **Falcon 9 na Polônia (2025)**, fragmentos em **aldeia no Quênia**, **Long March 5B** sobre Indonésia/Malásia (2022).
- Causa estrutural: megaconstelações deorbitando ao fim da vida útil → volume só cresce.

## 3. Por que importa (risco mensurável)

- **~10% de chance** de uma vítima humana por detrito de foguete na próxima década (Byers et al., *Nature Scientific Reports*, 2024).
- **~26%/ano** de detrito descontrolado cruzar espaço aéreo movimentado.
- Aviação: **Espanha e França fecharam espaço aéreo** por reentrada em 2022. Fechar espaço aéreo custa caro mesmo sem impacto — o risco já é **operacional**.
- **Equidade**: corpos de foguete sobrevoam mais as baixas latitudes → o **Sul Global** carrega risco desproporcional. Brasil (território enorme, baixa latitude, DECEA, Alcântara) é o caso de uso natural.

## 4. A lacuna

FAA (relatório ao Congresso), UNOOSA e IAA **pedem explicitamente** um sistema de aviso para afastar aeronaves e pessoas de detritos caindo. Hoje:

- Incumbentes (LeoLabs, Slingshot, COMSPOC, SpaceX Stargaze) focam **colisão em órbita** — caro, enterprise, "para cima".
- Aerospace CORDS é banco de dados de **especialista**.
- Não existe **alerta regional, grátis e acessível** para quem está no solo.

**WhereItFalls ocupa esse vão.**

## 5. A solução

Pipeline backend que vira produto:

1. **Ingest** — previsões de reentrada (Space-Track TIP) + elementos orbitais (CelesTrak) + histórico (Aerospace CORDS). Dado-fonte **gratuito**.
2. **Órbita** — `skyfield` propaga a órbita na janela de incerteza → *ground-track* (trilha no solo).
3. **Risco** — `shapely` + PostGIS geram o **corredor de risco** e cruzam com aeroportos, regiões e densidade populacional → **score**.
4. **Alerta** — mapa de calor (globo 3D + heatmap), e-mail e webhook para quem está sob a faixa de incerteza.

**Posicionamento**: apoio à decisão para autoridades (qual aeroporto/corredor/região está sob a faixa, para gerenciar espaço aéreo e priorizar resposta) — **não** alarme individual. Esse enquadramento responde à incerteza de ~±20% da previsão e é exatamente o que a literatura pede.

**Stack**: Python · FastAPI · skyfield/sgp4 · shapely/geopandas · PostgreSQL/PostGIS · React + Vite + globo 3D · Docker.

## 6. Mercado e clientes

- **Mercado SSA** (Space Situational Awareness): US$ 1,7–2,3 bi (2025/26) → US$ 2,8–5 bi (2030–34), CAGR ~7–10%.
- Compradores já existem: US Office of Space Commerce e UK Space Agency contratam SSA comercial.
- **COGS ~zero** (dado-fonte gratuito) → margem alta.

| Segmento | Uso |
|----------|-----|
| Defesa civil / DECEA / FAB | gerenciar espaço aéreo e resposta no solo |
| Aviação (companhias, aeroportos) | desvio de rota, awareness operacional |
| **Seguradoras** (aviação + responsabilidade espacial) | **score de risco + histórico para underwriting** |
| Marítimo / portos | risco sobre rotas e zonas de exclusão |

## 7. Modelo de negócio

API **freemium**:

- **Free** — leitura de reentradas, risco por região, mapa de calor, histórico (público, pesquisa, imprensa). Bem social + adoção.
- **Pro** — assinatura de alerta (e-mail/webhook), SLA, alerta por região (aviação, aeroportos, defesa civil).
- **Insurance** — score por ativo/apólice, analytics histórico, incerteza detalhada (seguradoras / underwriting).

## 8. Impacto

- **Segurança** de passageiros e de pessoas no solo — o aviso que falta hoje.
- **Equidade**: prioriza um território (Brasil/Sul Global) desatendido e mais exposto.
- **Acesso**: tier público gratuito democratiza um alerta hoje trancado em silos de defesa.

## 9. Diferencial

- **Society-facing**, não B2B-only: protege gente no chão e voos.
- **Não duplica** Stargaze/LeoLabs (que cuidam da órbita) — cuida do **solo**.
- **Brasil-first**: região desatendida e mais exposta.
- **Demanda institucional documentada** (FAA/UNOOSA/IAA) + dado gratuito.

## 10. Visão

Hoje: MVP Brasil (corredor de risco + heatmap + alerta). Próximo: webhooks, tier seguradoras, integração com despacho aéreo/defesa civil. Visão: malha de alerta multi-região + parcerias com autoridades de aviação.

---

*Fontes em [`RESEARCH.md`](RESEARCH.md). Arquitetura em [`ARCHITECTURE.md`](ARCHITECTURE.md).*
