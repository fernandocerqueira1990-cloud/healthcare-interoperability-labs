# Healthcare Interoperability Labs

> Evolução prática de estudos de interoperabilidade em saúde para um **Healthcare Integration Gateway** modular, reproduzível e preparado para evoluir de laboratório para PoC, MVP, piloto e produto.

Este repositório reúne duas frentes complementares:

1. **Laboratórios em Google Cloud Healthcare API** — HL7v2, FHIR, DICOM/DICOMweb, Pub/Sub, Dataflow e BigQuery.
2. **Healthcare Integration Gateway** — implementação local para receber, validar, transformar, rotear e persistir fluxos de interoperabilidade em saúde.

> Todos os exemplos públicos usam dados fictícios ou sintéticos.

---

## Status atual

**MVP v0.1 — Milestones 1.1, 1.2, 1.3 e 1.4 concluídos e validados**

### ✅ Milestone 1.1 — Ambiente FHIR Local

- HAPI FHIR R4 `8.10.0`;
- PostgreSQL `16-alpine`;
- Docker Compose;
- persistência em volume Docker;
- `CapabilityStatement` validado;
- `Patient` criado via REST;
- busca por `Patient.identifier` validada;
- persistência confirmada após recriação dos containers.

### ✅ Milestone 1.2 — HIS Simulator + HL7v2 ADT^A01

- mensagem HL7v2 `ADT^A01` sintética;
- segmentos `MSH`, `EVN`, `PID` e `PV1`;
- inspeção automatizada de campos;
- tratamento específico do parsing de `MSH`;
- validação estrutural mínima;
- happy path com `VALIDATION RESULT: PASS`;
- teste negativo controlado;
- troubleshooting de deslocamento de campos no `PV1`.

### ✅ Milestone 1.3 — Transporte MLLP + ACK/NACK

- MLLP Receiver em `127.0.0.1:2575`;
- HIS Simulator MLLP Client;
- TCP + framing MLLP;
- envio real de HL7v2 pelo simulador;
- extração da mensagem do buffer TCP;
- leitura de `MSH-9` e `MSH-10`;
- correlação por `Message Control ID`;
- `AA` — Application Accept;
- `AE` — Application Error;
- `AR` — Application Reject;
- logs operacionais;
- testes positivos e negativos;
- troubleshooting de delimitador adicional no `MSH`.

### ✅ Milestone 1.4 — HL7 Parser + Validator Core desacoplados

- `ParsedHL7Message` como contrato interno do core;
- Parser HL7 reutilizável e independente do transporte;
- tratamento específico de `MSH-1` / `MSH-2`;
- separador de campos propagado a partir de `MSH-1`;
- Validator Core independente de socket/MLLP;
- decisão estruturada de `AA`, `AE` e `AR`;
- Receiver refatorado para transporte + orquestração;
- 6 testes automatizados de regressão;
- testes ponta a ponta MLLP preservados sem regressão.

### 🔜 Próximo: Milestone 1.5 — ADT^A01 → FHIR Patient + Encounter

Objetivos:

- mapear `PID` para `Patient`;
- mapear `PV1` para `Encounter`;
- manter rastreabilidade entre mensagem HL7 e resources FHIR;
- validar payloads FHIR R4 antes do envio ao HAPI FHIR.

---

## Arquitetura do produto

A arquitetura abaixo representa o estado atual do MVP v0.1 e separa o que já está implementado do que ainda será construído.

```mermaid
flowchart LR
    subgraph IMPLEMENTADO[Implementado e validado]
        A[HIS Simulator / ADT^A01]
        B[HL7 Inspector]
        C[Structural Validator]
        D[MLLP Receiver]
        E[ACK AA / AE / AR]
        G[HAPI FHIR R4]
        H[(PostgreSQL)]

        A --> B
        A --> C
        A -->|TCP / MLLP| D
        D --> E
        E -->|ACK / MLLP| A
        G -->|JDBC| H
    end

    subgraph PROXIMO[Milestone 1.4]
        P[HL7 Parser]
        V[Validator Core]
        D -.-> P
        P -.-> V
    end

    subgraph PLANEJADO[Pipeline planejado]
        T[HL7 to FHIR Transformer]
        R[Router]
        L[Audit / Logs estruturados]

        V -.-> T
        T -.-> R
        R -.->|REST FHIR| G

        D -.-> L
        P -.-> L
        V -.-> L
        T -.-> L
        R -.-> L
    end
```

### Legenda de status

| Componente | Status atual |
|---|---|
| HIS Simulator / mensagem ADT^A01 | ✅ Implementado |
| HL7 Inspector | ✅ Implementado |
| Structural Validator | ✅ Implementado |
| MLLP Receiver | ✅ Implementado |
| ACK AA / AE / AR | ✅ Implementado |
| HAPI FHIR R4 | ✅ Implementado |
| PostgreSQL / persistência | ✅ Implementado |
| HL7 Parser desacoplado | ✅ Implementado |
| Validator Core desacoplado | ✅ Implementado |
| HL7 → FHIR Transformer | ⏳ Planejado |
| Router | ⏳ Planejado |
| Audit / Logs estruturados | ⏳ Planejado |

### Fluxo implementado atualmente

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
      |
      v
HIS Simulator

HAPI FHIR R4
      |
      | JDBC
      v
PostgreSQL
      |
      v
Docker Volume
```

> O fluxo MLLP e o bloco FHIR ainda não estão conectados ponta a ponta. Essa conexão será construída progressivamente nos próximos milestones.

### Arquitetura alvo do MVP v0.1

```text
HIS Simulator
      |
      | HL7v2 ADT^A01 / MLLP
      v
MLLP Receiver
      |
      v
HL7 Parser
      |
      v
Validator Core
      |
      v
HL7 -> FHIR Transformer
      |
      | Patient + Encounter
      v
Router
      |
      | REST FHIR
      v
HAPI FHIR R4
      |
      v
PostgreSQL

Todos os componentes críticos
      |
      `--> Audit / Logs
```

---

## Roadmap

| Etapa | Escopo | Status |
|---|---|---|
| MVP v0.1 / 1.1 | Ambiente FHIR local — HAPI FHIR + PostgreSQL | ✅ Concluído |
| MVP v0.1 / 1.2 | HIS Simulator + HL7v2 ADT^A01 | ✅ Concluído |
| MVP v0.1 / 1.3 | Transporte MLLP + ACK/NACK | ✅ Concluído |
| MVP v0.1 / 1.4 | Parser + Validator HL7v2 | ✅ Concluído |
| MVP v0.1 / 1.5 | ADT^A01 → FHIR Patient + Encounter | Planejado |
| MVP v0.1 / 1.6 | Pipeline end-to-end | Planejado |
| v0.2 | ORM / ORU → ServiceRequest / Observation / DiagnosticReport | Planejado |
| v0.3 | REST API Gateway e webhooks | Planejado |
| v0.4 | Dashboard operacional | Planejado |
| v0.5 | Configuração multi-cliente | Planejado |
| v0.6 | Observabilidade avançada | Planejado |
| v0.7 | DICOM / DICOMweb | Planejado |
| v0.8 | Rules Engine | Planejado |
| v0.9 | Assistente de troubleshooting com IA | Planejado |
| v1.0 | Piloto controlado / plataforma de referência | Futuro |

---

## Documentação

A regra do projeto é:

**teoria → motivo → implementação → teste → validação → troubleshooting → evidência**

### Produto e arquitetura

- [Índice da documentação](docs/README.md)
- [Product Vision](docs/product-vision.md)
- [Arquitetura v0.1](docs/architecture/01-overview.md)
- [Fluxo ADT^A01 → FHIR](docs/architecture/02-adt-a01-flow.md)
- [Fluxo MLLP + ACK](docs/architecture/03-mllp-ack-flow.md)
- [Status do projeto](docs/project-status.md)

### Implementação

- [01 — Ambiente FHIR local](docs/implementation/01-local-fhir-environment.md)
- [02 — HIS Simulator + HL7v2 ADT^A01](docs/implementation/02-his-simulator-adt-a01.md)
- [03 — Transporte MLLP + ACK/NACK](docs/implementation/03-mllp-transport-ack-nack.md)
- [04 — HL7 Parser + Validator Core](docs/implementation/04-hl7-parser-validator-core.md)

### Evidências

- [Validação do ambiente FHIR local](docs/evidence/mvp-v0.1-local-fhir-validation.md)
- [Validação do HIS Simulator / ADT^A01](docs/evidence/mvp-v0.1-his-simulator-validation.md)
- [Validação MLLP + ACK/NACK](docs/evidence/mvp-v0.1-mllp-ack-validation.md)
- [Validação do HL7 Parser + Validator Core](docs/evidence/mvp-v0.1-hl7-parser-validator-validation.md)

### Relatórios

- [Milestone 1.1](docs/reports/01-milestone-1.1-summary.md)
- [Milestone 1.2](docs/reports/02-milestone-1.2-summary.md)
- [Milestone 1.3](docs/reports/03-milestone-1.3-summary.md)
- [Milestone 1.4](docs/reports/04-milestone-1.4-summary.md)

### Guia de estudo

- [InterSystems Technical Specialist — Guia de estudo](docs/study/intersystems-technical-specialist-interview-guide.md)

### Labs Google Cloud

- [Ingesting HL7v2](docs/01-ingesting-hl7v2.md)
- [Streaming HL7v2 to FHIR](docs/02-streaming-hl7v2-to-fhir.md)
- [Ingesting DICOM](docs/03-ingesting-dicom.md)
- [Ingesting FHIR](docs/04-ingesting-fhir.md)

---

## Executando o laboratório

### Subir HAPI FHIR + PostgreSQL

```bash
cd docker
docker compose up -d
```

### Verificar serviços

```bash
docker compose ps
```

### Inspecionar ADT^A01

```bash
python3 src/his-simulator/tools/inspect_hl7.py
```

### Validar ADT^A01

```bash
python3 src/his-simulator/tools/validate_adt_a01.py
```

### Executar o MLLP Receiver

```bash
python3 -m src.gateway.receivers.mllp_receiver
```

> O Receiver é executado como módulo para que os imports internos do pacote `src` sejam resolvidos de forma consistente.

### Enviar a mensagem válida

Em outro terminal:

```bash
python3 src/his-simulator/tools/send_mllp.py
```

Resultado esperado:

```text
ACK TYPE: AA - Application Accept
ACK VALIDATION RESULT: PASS
```

### Testar AE

```bash
python3 src/his-simulator/tools/send_mllp.py \
src/his-simulator/messages/adt_a01_invalid.hl7
```

### Testar AR

```bash
python3 src/his-simulator/tools/send_mllp.py \
src/his-simulator/messages/orm_o01_unsupported.hl7
```

---

## Estrutura atual

```text
healthcare-interoperability-labs/
├── README.md
├── LICENSE
├── docker/
│   ├── docker-compose.yml
│   └── hapi.application.yaml
├── src/
│   ├── gateway/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── hl7_parser.py
│   │   │   └── hl7_validator.py
│   │   └── receivers/
│   │       └── mllp_receiver.py
│   └── his-simulator/
│       ├── messages/
│       │   ├── adt_a01.hl7
│       │   ├── adt_a01_invalid.hl7
│       │   └── orm_o01_unsupported.hl7
│       └── tools/
│           ├── inspect_hl7.py
│           ├── validate_adt_a01.py
│           └── send_mllp.py
├── docs/
│   ├── README.md
│   ├── product-vision.md
│   ├── project-status.md
│   ├── architecture/
│   │   ├── 01-overview.md
│   │   ├── 02-adt-a01-flow.md
│   │   └── 03-mllp-ack-flow.md
│   ├── implementation/
│   │   ├── 01-local-fhir-environment.md
│   │   ├── 02-his-simulator-adt-a01.md
│   │   └── 03-mllp-transport-ack-nack.md
│   ├── evidence/
│   │   ├── mvp-v0.1-local-fhir-validation.md
│   │   ├── mvp-v0.1-his-simulator-validation.md
│   │   └── mvp-v0.1-mllp-ack-validation.md
│   └── reports/
│       ├── 01-milestone-1.1-summary.md
│       ├── 02-milestone-1.2-summary.md
│       ├── 03-milestone-1.3-summary.md
│       └── 04-milestone-1.4-summary.md
├── tests/
│   └── gateway/
│       └── test_hl7_core.py
└── assets/
    └── README.md
```

---

## Princípios técnicos

- modularidade;
- baixo acoplamento;
- configuração por cliente;
- dados sintéticos em ambiente público;
- infraestrutura reproduzível;
- validação incremental;
- documentação junto com código;
- troubleshooting documentado;
- observabilidade como requisito arquitetural.

---

## Competências praticadas

- Healthcare IT e interoperabilidade;
- HL7v2 / ADT^A01;
- MLLP / TCP sockets;
- ACK HL7v2 / `MSA`;
- parsing e validação estrutural;
- FHIR R4;
- HAPI FHIR;
- PostgreSQL;
- Docker / Docker Compose;
- Python;
- REST APIs;
- DICOM / DICOMweb;
- Google Cloud Healthcare API;
- arquitetura de integração hospitalar;
- troubleshooting e validação técnica.
