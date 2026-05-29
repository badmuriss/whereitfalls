# Roteiro — Vídeo de Demonstração (Parte 2) · ESQUELETO

**Duração alvo:** 4:00 (limite FIAP — compõe a nota GS1)
**Formato:** screencast do protótipo rodando local + narração
**Tom:** técnico curto, mostrando o que funciona.
**Status:** esqueleto — preencher os blocos `[PREENCHER]` quando o protótipo estiver rodando.

Estrutura segue o método da Parte 1 e dos roteiros da `vigilante-ai/docs`: blocos de tempo, narração em `>`, direção de cena em `[...]`, `//pausa//`.

> A Parte 2 exige **demonstração do protótipo funcionando** (tela rodando, ação interativa, trecho de código). Não basta slide.

---

## Divisão de tempo (240s)

| Bloco | Tempo | Dur | Conteúdo |
|---|---|---|---|
| 1 — Capa + problema | 0:00 → 0:25 | 25s | gancho curto (reusar Parte 1 condensado) |
| 2 — Stack & arquitetura | 0:25 → 0:50 | 25s | mostrar `docker compose ps` / diagrama |
| 3 — Ingest de dados reais | 0:50 → 1:25 | 35s | reentrada real do Space-Track no sistema |
| 4 — Globo 3D + corredor de risco | 1:25 → 2:15 | 50s | **o "uau"** — órbita + ground-track + corredor |
| 5 — Mapa de calor (Brasil) | 2:15 → 2:50 | 35s | heatmap de risco por região/aeroporto |
| 6 — Alerta (webhook) | 2:50 → 3:25 | 35s | assinar região (webhook) → payload do alerta |
| 7 — API / Swagger | 3:25 → 3:50 | 25s | mostrar `/docs` e um endpoint respondendo |
| 8 — Fechamento + próximos passos | 3:50 → 4:00 | 10s | impacto + visão |

---

## SCRIPT (preencher)

### [0:00 — Bloco 1 — Capa + problema]
[Landing/dashboard no localhost]
> Somos o grupo do WhereItFalls. Nesta fase entregamos o protótipo funcional, então em vez de slide, vamos mostrar o sistema rodando.
> //pausa//
> O problema: detritos espaciais caem cada vez mais — e ninguém avisa quem está no solo. `[ajustar 1 frase de contexto]`

### [0:25 — Bloco 2 — Stack & arquitetura]
[Terminal: `docker compose ps`]
> O protótipo roda com **FastAPI + PostGIS** no back, **React + Vite** com globo 3D no front, **skyfield** pra órbita e **shapely/PostGIS** pro risco. Tudo em containers, local.
> `[PREENCHER: confirmar serviços que aparecem no compose]`

### [0:50 — Bloco 3 — Ingest de dados reais]
[Mostrar ingest / lista de reentradas no painel]
> `[PREENCHER: mostrar uma reentrada real vinda do Space-Track TIP — objeto, janela prevista, incerteza]`
> Aqui não é dado fake: é a previsão oficial de reentrada, com a janela de incerteza.

### [1:25 — Bloco 4 — Globo 3D + corredor de risco] ★ destaque
[Globo 3D em tela cheia]
> `[PREENCHER: mostrar a órbita do objeto, o ground-track previsto e o corredor de incerteza desenhado sobre o globo]`
> //pausa//
> Essa faixa é o corredor de risco — onde o objeto pode reentrar. Os pontos em âmbar são aeroportos e regiões sob a faixa.

### [2:15 — Bloco 5 — Mapa de calor (Brasil)]
[Aba de heatmap]
> `[PREENCHER: heatmap de risco sobre o Brasil; explicar intensidade = score × exposição]`
> Foco no Brasil: baixa latitude, mais sobrevoos, e ninguém atende essa região.

### [2:50 — Bloco 6 — Alerta]
[Assinar uma região → disparar]
> `[PREENCHER: criar assinatura de uma região (canal webhook) via API; mostrar o payload do webhook (JSON com corredor + score)]`
> O alerta vai pra quem precisa decidir: defesa civil, aeroporto, seguradora.

### [3:25 — Bloco 7 — API / Swagger]
[`localhost:8000/docs`]
> `[PREENCHER: abrir Swagger, executar GET /v1/reentries ou /v1/risk ao vivo]`
> O produto é uma API: qualquer sistema integra via REST ou webhook.

### [3:50 — Bloco 8 — Fechamento]
> Resumindo: ingest de reentrada real, corredor de risco no globo, heatmap por região, alerta multicanal e API aberta. Próximo passo: tier para seguradoras e cobertura multi-região. Link no entregável. Obrigado.

[Fim — 4:00]

---

## Notas de preenchimento
- Pré-popular o banco com **1–2 reentradas reais** (ou seed realista) pra demo não ficar vazia.
- Ter **1 região assinada** pronta pra disparar o alerta ao vivo.
- Se o globo 3D pesar na gravação, congelar o frame em pós.
- Mostrar **dado real** (Space-Track) pelo menos uma vez — é a prova de que funciona.

## Se estourar 4:00 (cortes)
1. Bloco 7 (Swagger) → reduzir a 1 frase (−12s).
2. Bloco 2 (stack) → 1 frase (−10s).

## Checklist de gravação
- [ ] `docker compose up` com tudo UP (`docker compose ps`).
- [ ] Banco com reentrada(s) e 1 região assinada.
- [ ] Globo 3D renderizando suave.
- [ ] Webhook de teste configurado e testado.
- [ ] Browser fullscreen, zoom 100%, sem extensão visível.
- [ ] Áudio testado; cronômetro visível.
- [ ] Publicar no YouTube; link no `.txt` do entregável.
