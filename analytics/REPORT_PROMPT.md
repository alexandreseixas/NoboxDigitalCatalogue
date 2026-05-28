# RANTUGUESSER — Prompt para Geração de Relatório

Copie tudo abaixo e cole numa nova conversa com o Claude (ou ChatGPT / Gemini). Anexe também o ficheiro `events.csv` exportado pelo script Python.

---

## CONTEXTO

És um analista de dados a produzir um relatório executivo para a equipa de marketing da Bial sobre o desempenho do RANTUGUESSER — um jogo educacional digital integrado num CLM (Closed Loop Marketing) usado pelos delegados comerciais em visitas a profissionais de saúde (HCPs) em Portugal.

O produto promovido é o **Rantudil® (acemetacina)** — um AINE com perfil de segurança e via metabólica diferenciada relativamente a outros AINEs.

O jogo tem 3 desafios curtos sobre conhecimento clínico-farmacológico, com debrief educativo após cada um. O delegado mostra-o no iPad ao HCP durante a visita.

## ESTRUTURA DO JOGO (importante para interpretar os dados)

1. **Privacy** — aviso de privacidade (1º ecrã)
2. **Register** — registo do HCP (tipo, ULS/Grupo, instituição)
3. **Intro** — ecrã de boas-vindas
4. **C1 — Escada Analgésica** — o HCP coloca 3 cartas nos 3 escalões corretos da escada analgésica da OMS
5. **D1** — debrief de C1
6. **C2 — Farmacovigilância** — o HCP indica num slider quantos *reports* de farmacovigilância a Acemetacina teve em Portugal
7. **D2** — debrief de C2
8. **C3 — Via Metabólica** — o HCP arrasta o comprimido para a via metabólica preferencial (Fase I ou Fase II)
9. **D3** — debrief de C3
10. **Finale** — ecrã final com pontuação
11. **IEC** — documento de Informação Essencial Conforme
12. **Credits** — créditos

## RESPOSTAS CORRETAS

- **C1**: as 3 cartas corretas, na ordem dos slots 0→1→2, são:
  - Slot 0: card_id **0** → "AINEs / Paracetamol"
  - Slot 1: card_id **1** → "AINEs + Opióides fracos"
  - Slot 2: card_id **2** → "AINEs + Opióides fortes"
  - (Cartas 3 "Paracetamol" e 4 "Opióides fortes" são distratores — NÃO devem aparecer em nenhum slot)
- **C2**: valor correto = **1.3** *reports* por milhão de vendas (Acemetacina/Rantudil®). O slider é **contínuo** com range 0–50. Referências comparativas mostradas no jogo: Naproxeno 11.9, Etoricoxib 16.4, Diclofenac 31.0, Ibuprofeno ~48.3. Considera-se "correto" quando `score >= 80` no payload (= guess dentro de ±1.07 do alvo). **NÃO USES `payload.correct` para C2** — versões iniciais do jogo tinham um bug que marcava `correct: guessVal === 28`. Calcula a correção a partir de `payload.score >= 80` ou de `abs(guess - 1.3) < 1.07`.
- **C3**: zona correta = **'p2'** (= Fase II — Glucoronoconjugação). 'p1' = Fase I (errado)

## ESQUEMA DOS DADOS

O ficheiro `events.csv` tem estas colunas:

| Coluna | Tipo | Descrição |
|---|---|---|
| `session_id` | uuid string | identifica unicamente uma sessão de jogo |
| `institution` | string | instituição registada pelo HCP (vazio antes de register_complete) |
| `event_type` | string | um dos 7 tipos abaixo |
| `payload` | JSON string | dados específicos do evento — precisa de `json.loads()` ou equivalente |
| `client_ts` | int (ms) | timestamp do cliente em milissegundos |
| `server_ts` | ISO timestamp | timestamp do servidor (UTC) |

### Tipos de evento e seus payloads

**`session_start`** — uma sessão começou (carregamento da página, restart)
```json
{
  "device": {
    "os": "ios" | "android" | "macos" | "windows" | "unknown",
    "form": "tablet" | "phone" | "desktop",
    "sw": 1024, "sh": 768,        // screen size
    "iw": 980, "ih": 720,          // viewport size
    "dpr": 2,                       // device pixel ratio
    "touch": true,
    "ua": "Mozilla/5.0..."         // user agent (truncado a 200 chars)
  }
}
```

**`screen_enter`** — utilizador transitou para um novo ecrã
```json
{
  "from": "privacy",                // ecrã que está a sair
  "to": "register",                  // ecrã onde entra
  "prev_screen_ms": 4321,            // tempo passado no ecrã anterior
  "session_ms": 4321                 // tempo total da sessão até agora
}
```

**`c1_answer`** — utilizador clicou "Verificar" no Desafio 1 (cada tentativa)
```json
{
  "slots": [0, 1, 2],                // IDs das cartas colocadas em cada slot
  "correct_count": 3,                // 0 a 3 — quantos slots têm a carta certa
  "correct": true,                   // true se acertou os 3
  "score": 100,                      // pontos ganhos
  "tries": 1                         // número de tentativas até agora
}
```

**`c2_answer`** — utilizador clicou "Confirmar" no Desafio 2
```json
{
  "guess": 1.3,                      // valor escolhido no slider (float, range 0..50)
  "correct": true,                   // ⚠️ ignorar — early bug; usa score >= 80
  "score": 100                       // 100 no alvo (1.3), decai quadraticamente, 0 a 10.6+ de distância
}
```

**`c3_answer`** — utilizador largou o comprimido numa zona (Desafio 3)
```json
{
  "zone": "p1" | "p2",               // p2 = Fase II = correto; p1 = Fase I = errado
  "correct": true,                   // true se zone === "p2"
  "score": 100
}
```

**`register_complete`** — utilizador completou o registo
```json
{
  "t_register_ms": 18432,            // tempo total no ecrã de registo
  "friction": {
    "typeFocusMs": 1200,             // tempo total focado no campo "Tipo"
    "typeFocusCount": 1,             // nº de vezes que focou o campo
    "ulsFocusMs": 800,
    "ulsFocusCount": 1,
    "instFocusMs": 14000,
    "instFocusCount": 2,
    "instInputCount": 23             // nº de teclas digitadas na pesquisa
  },
  "type": "public" | "private",      // tipo de profissional
  "has_uls": true, "has_inst": true
}
```

**`session_complete`** — utilizador chegou ao Finale
```json
{
  "t_total_ms": 187432,              // duração total da sessão
  "scores": [100, 80, 100],          // [c1, c2, c3]
  "total_score": 280
}
```

## ANÁLISES A PRODUZIR

Produz um relatório executivo em **HTML autocontido** (CSS inline, sem dependências externas, pronto a abrir num browser), na **língua portuguesa de Portugal**, com identidade visual sóbria e profissional (paleta sugerida: teal `#1D5C62`, âmbar `#F5A800`, creme `#F5F1E8`, branco). Inclui as secções abaixo, por esta ordem:

### 1. Sumário Executivo (KPIs)
4 cartões grandes:
- Sessões iniciadas (total `session_start`)
- Sessões completas (total `session_complete`)
- Taxa de conclusão (%)
- Duração média de sessão completa (mm:ss)

### 2. Funil de Engagement
Gráfico horizontal (CSS bars, sem libraries externas) mostrando quantas sessões atingiram cada ecrã do funil: `privacy → register → intro → c1 → d1 → c2 → d2 → c3 → d3 → finale`. Mostra % cumulativa em cada passo e identifica visualmente o **maior ponto de queda**.

### 3. Conhecimento Prévio dos HCPs (a métrica mais importante)
Três barras horizontais com a **% de respostas corretas à primeira tentativa** para C1, C2 e C3. Acompanha cada barra com:
- O n (número de sessões que chegaram a esse desafio)
- Uma frase de interpretação (ex: "70% dos HCPs já dominam a escada analgésica")

### 4. C1 — Distribuição de Cartas por Slot (primeira tentativa)
Tabela ou gráfico mostrando, para cada slot (0/1/2), a frequência de cada carta colocada. Destaca os erros mais comuns. Indica explicitamente qual a carta correta em cada slot.

### 5. C2 — Histograma dos Palpites
Histograma da distribuição de palpites (eixo X: valor 0–50 em bins de 1, eixo Y: nº de respostas). Marca claramente o valor correto (1.3) e, se possível, os valores de referência dos comparadores (Naproxeno 11.9, Etoricoxib 16.4, Diclofenac 31.0). Calcula:
- Mediana, média e moda (arredondada) dos palpites
- % dentro da banda correta (±1.07 do alvo)
- % que sobrestimam (> 2.37) vs subestimam (< 0.23)
- Interpreta a tendência: a história é provavelmente que os HCPs **sobrestimam** o volume de reports da Acemetacina por não saberem o seu perfil de segurança superior — o que é uma oportunidade direta de comunicação para o Rantudil®.

### 6. C3 — Via Metabólica Escolhida
% que escolheu Fase II (correto) vs Fase I (errado) à primeira tentativa.

### 7. Tempo Médio por Ecrã
Tabela ou gráfico de barras: para cada ecrã, tempo médio em segundos (calculado a partir de `screen_enter.prev_screen_ms`). Filtra outliers (> 30 min). Comenta sobretudo o tempo nos **debriefs** (d1/d2/d3) — é o proxy mais direto para "estão a ler a informação científica?".

### 8. Fricção no Registo
- Tempo médio total no ecrã de registo
- Tempo médio em cada campo (typeFocusMs, ulsFocusMs, instFocusMs)
- Nº médio de teclas digitadas na pesquisa de instituição
- Identifica o campo mais "pesado" e sugere se justifica polish adicional

### 9. Distribuição de Dispositivos
% das sessões por `os/form` (ex: "ios/tablet 87%"). Útil para confirmar que o jogo é maioritariamente jogado em iPad.

### 10. Top 15 Instituições
Tabela com:
| Instituição | Sessões iniciadas | Sessões completas | Score médio |

Ordenado por sessões iniciadas (descendente).

### 11. Taxa de Restart
% de sessões completas onde o utilizador voltou ao ecrã `privacy` depois do finale (sinal de replay value / engagement).

### 12. Recomendações
Bullet points curtos (3–5) com acções concretas para a equipa de marketing, com base nos dados. Ex:
- "70% dos HCPs erram a posição da carta X → reforçar X na visita."
- "Tempo médio em d2 é de apenas 4s → o debrief de farmacovigilância não está a ser absorvido; considerar tornar a informação mais visual."

## REGRAS IMPORTANTES

1. **Não inventes dados.** Se um cálculo der zero amostras, escreve explicitamente "sem dados".
2. **Filtra outliers** — qualquer `prev_screen_ms` > 30 min ou `t_total_ms` > 1 h é provavelmente uma sessão deixada aberta; exclui-os das médias.
3. **A primeira tentativa de cada desafio é o que conta para "conhecimento prévio"** — ignora tentativas subsequentes (o jogo só permite uma tentativa por desafio, mas se houver duplicados por bug, fica com a primeira por `client_ts`).
4. **Para a taxa de conclusão**, denominador = `session_start` events. Numerador = `session_complete` events.
5. **Privacidade**: não há PII para além de `institution`. Não tentes derivar identidades pessoais.
6. **Tom**: factual, conciso, accionável. Esta é uma audiência executiva — sem jargão técnico.
7. **HTML autocontido**: tudo numa só página, com CSS inline. Gráficos podem ser feitos com `<div>` + CSS (barras horizontais), `<table>` para distribuições, ou SVG inline para histogramas. Não dependas de Chart.js / D3 / fontes externas.
8. **Imprimível**: inclui `@media print` para que a página fique apresentável quando exportada para PDF.

## OUTPUT

Devolve o HTML completo num único bloco de código, pronto a guardar como `report.html` e abrir no browser. Não incluas explicações fora do HTML — só o ficheiro.
