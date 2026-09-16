# Status do Projeto — Healthcare Integration Gateway

## Situação atual

O projeto está na fase **MVP v0.1**.

- **Milestone 1.1 — Ambiente FHIR Local:** ✅ concluído e validado.
- **Milestone 1.2 — HIS Simulator + HL7v2 ADT^A01:** ✅ concluído e validado.
- **Milestone 1.3 — Transporte MLLP + ACK/NACK:** ✅ concluído e validado.
- **Milestone 1.4 — HL7 Parser + Validator Core desacoplados:** 🔜 próximo passo.

---

## Milestone 1.1 — Ambiente FHIR Local

### Objetivo

Criar um destino FHIR local, persistente e reproduzível antes de implementar o pipeline HL7v2 → FHIR.

### Componentes implementados

- HAPI FHIR R4 `8.10.0`;
- PostgreSQL `16-alpine`;
- Docker Compose;
- rede interna entre containers;
- volume persistente;
- configuração JDBC HAPI FHIR → PostgreSQL.

### Validações executadas

```text
[x] PostgreSQL saudável
[x] HAPI FHIR em execução
[x] CapabilityStatement retornado por /fhir/metadata
[x] HTTP 200 no endpoint de metadata
[x] Patient sintético criado via REST
[x] HTTP 201 na criação do Patient
[x] Patient recuperado por identifier
[x] Bundle searchset com total = 1
[x] Persistência comprovada após docker compose down/up
```

---

## Milestone 1.2 — HIS Simulator + HL7v2 ADT^A01

### Objetivo

Introduzir o sistema de origem do laboratório e validar uma mensagem HL7v2 `ADT^A01` antes de implementar transporte MLLP.

### Implementado e validado

```text
[x] estrutura src/his-simulator/
[x] mensagem ADT^A01 sintética
[x] segmentos MSH, EVN, PID e PV1
[x] utilitário de inspeção de campos
[x] tratamento específico de MSH-1/MSH-2
[x] validação estrutural mínima
[x] happy path PASS
[x] teste negativo controlado
[x] troubleshooting de deslocamento de campos PV1
```

---

## Milestone 1.3 — Transporte MLLP + ACK/NACK

### Objetivo

Adicionar uma interface real de entrada HL7v2 via TCP/MLLP e responder ao emissor com ACK coerente com o resultado do processamento inicial.

### Componentes implementados

- `src/gateway/receivers/mllp_receiver.py`;
- `src/his-simulator/tools/send_mllp.py`;
- mensagem `ADT^A01` inválida para teste de `AE`;
- mensagem `ORM^O01` não suportada para teste de `AR`;
- `.gitignore` para artefatos Python.

### Transporte validado

```text
[x] socket TCP
[x] bind em 127.0.0.1:2575
[x] conexão HIS Simulator -> Gateway
[x] framing MLLP 0x0B ... 0x1C 0x0D
[x] extração de mensagem do buffer
[x] ACK retornado pelo mesmo transporte
```

### Parsing mínimo usado no milestone

O Receiver extrai atualmente os metadados necessários do `MSH` para provar transporte e acknowledgement:

- `MSH-9` — Message Type;
- `MSH-10` — Message Control ID;
- `MSH-11` — Processing ID;
- `MSH-12` — Version ID;
- aplicações e facilities de origem/destino para construção do ACK.

Essa responsabilidade será desacoplada no Milestone 1.4.

### ACKs validados

#### AA — Application Accept

Entrada:

```text
MSH-9  = ADT^A01
MSH-10 = MSG00001
```

Resposta:

```text
MSA|AA|MSG00001|Message accepted
ACK VALIDATION RESULT: PASS
```

#### AE — Application Error

Entrada:

```text
MSH-9  = ADT^A01
MSH-10 = vazio
```

Resposta:

```text
MSA|AE||Missing Message Control ID
ACK VALIDATION RESULT: PASS
```

#### AR — Application Reject

Entrada:

```text
MSH-9  = ORM^O01
MSH-10 = MSG00002
```

Resposta:

```text
MSA|AR|MSG00002|Unsupported message type
ACK VALIDATION RESULT: PASS
```

### Troubleshooting registrado

Durante o cenário de `AE`, um separador `|` adicional no `MSH` deslocou os campos seguintes.

Sintoma observado:

```text
type=
control_id=ADT^A01
```

A inspeção dos índices mostrou que `ADT^A01` havia sido deslocado para a posição lida como `MSH-10`.

Após correção:

```text
type=ADT^A01
control_id=<missing>
```

E o Receiver passou a gerar corretamente `AE`.

### Fluxo implementado após o Milestone 1.3

```text
HIS Simulator
      |
      | HL7v2 / TCP / MLLP
      v
MLLP Receiver
      |
      +--> MSH metadata
      +--> AA / AE / AR
      |
      v
ACK via MLLP
```

Destino FHIR já disponível, ainda separado do fluxo MLLP:

```text
HAPI FHIR R4
      |
      v
PostgreSQL
```

---

## Próximo milestone

### Milestone 1.4 — HL7 Parser + Validator Core desacoplados

Objetivos:

1. extrair parsing HL7v2 do MLLP Receiver;
2. criar parser reutilizável;
3. criar Validator Core independente do transporte;
4. reutilizar e evoluir as validações do Milestone 1.2;
5. manter decisão de ACK baseada no resultado do pipeline;
6. ampliar testes unitários/negativos;
7. preparar o caminho para o Transformer HL7 → FHIR.

Fluxo alvo:

```text
HIS Simulator
      |
      | MLLP
      v
MLLP Receiver
      |
      v
HL7 Parser
      |
      v
Validator Core
      |
      +--> ACK decision
      |
      v
Transformer (Milestone 1.5)
```

---

## Evolução prevista

```text
LAB
 |
 v
PoC
 |
 v
MVP
 |
 v
Piloto
 |
 v
Produto
```

O foco permanece em construir uma solução tecnicamente sólida, explicável, reproduzível e progressivamente aplicável a cenários reais de Healthcare IT.
