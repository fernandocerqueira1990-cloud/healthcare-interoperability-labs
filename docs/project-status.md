# Status do Projeto — Healthcare Integration Gateway

## Situação atual

O projeto está na fase **MVP v0.1**.

- **Milestone 1.1 — Ambiente FHIR Local:** concluído e validado.
- **Milestone 1.2 — HIS Simulator + HL7v2 ADT^A01:** concluído e validado.
- **Milestone 1.3 — Transporte MLLP + ACK/NACK:** próximo passo.

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
[x] validação de MSH-9 = ADT^A01
[x] validação de Message Control ID
[x] validação de versão HL7
[x] validação de Patient Identifier
[x] validação de Patient Name
[x] validação de Patient Class
[x] validação de Visit Number
[x] validação de Admit Date/Time
[x] happy path com resultado PASS
[x] teste negativo com remoção de PV1-19
[x] detecção do erro com resultado FAIL
[x] restauração da mensagem
[x] revalidação com resultado PASS
[x] troubleshooting de deslocamento de campos PV1
```

### Troubleshooting registrado

Durante a construção inicial, `Visit Number` foi posicionado em `PV1-18` e `Admit Date/Time` ficou deslocado. A causa foi a quantidade incorreta de delimitadores vazios no segmento `PV1`.

Após correção e inspeção automatizada:

```text
PV1-19 = Visit Number
PV1-44 = Admit Date/Time
```

O teste negativo controlado removeu `PV1-19`, gerando:

```text
[ERROR] PV1-19 (Visit Number) vazio ou ausente
VALIDATION RESULT: FAIL
```

Após restauração:

```text
VALIDATION RESULT: PASS
```

### Conceitos consolidados

- HL7v2 orientado a mensagens/eventos;
- `ADT` = Admission, Discharge and Transfer;
- `A01` = admissão/visit notification;
- `MSH` = Message Header;
- `EVN` = Event Type;
- `PID` = Patient Identification;
- `PV1` = Patient Visit;
- diferença entre Patient Identifier e Visit Number;
- importância posicional dos delimitadores HL7;
- parsing especial de `MSH`;
- distinção entre inspeção e validação;
- relação conceitual `PID → FHIR Patient` e `PV1 → FHIR Encounter`.

---

## Fluxo implementado até o momento

```text
HIS Simulator
      |
      v
HL7v2 ADT^A01
      |
      +--> Inspector
      |
      `--> Structural Validator
              |
              +--> PASS
              `--> FAIL
```

Destino FHIR já disponível do Milestone 1.1:

```text
HAPI FHIR R4
      |
      v
PostgreSQL
```

---

## Próximo milestone

### Milestone 1.3 — Transporte MLLP + ACK/NACK

Objetivos:

1. criar receptor MLLP;
2. transmitir a mensagem ADT^A01;
3. interpretar framing MLLP;
4. gerar ACK positivo;
5. gerar respostas de erro quando aplicável;
6. correlacionar ACK com Message Control ID;
7. registrar logs e evidências de transporte.

Fluxo alvo:

```text
HIS Simulator
      |
      | HL7v2 ADT^A01 / MLLP
      v
MLLP Receiver
      |
      v
Parser -> Validator
      |
      +--> ACK/NACK
      |
      v
Transformer -> FHIR Patient + Encounter
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
