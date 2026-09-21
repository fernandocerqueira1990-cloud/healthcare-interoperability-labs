# Status do Projeto — Healthcare Integration Gateway

## Situação atual

O projeto está na fase **MVP v0.1**.

- **Milestone 1.1 — Ambiente FHIR Local:** ✅ concluído e validado.
- **Milestone 1.2 — HIS Simulator + HL7v2 ADT^A01:** ✅ concluído e validado.
- **Milestone 1.3 — Transporte MLLP + ACK/NACK:** ✅ concluído e validado.
- **Milestone 1.4 — HL7 Parser + Validator Core desacoplados:** ✅ concluído e validado.
- **Milestone 1.5 — ADT^A01 → FHIR Patient + Encounter:** ✅ concluído e validado.\n- **Milestone 1.6 — End-to-end hardening e confiabilidade:** 🔜 próximo passo.

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

## Milestone 1.4 — HL7 Parser + Validator Core desacoplados

### Objetivo

Separar transporte, parsing e validação para reduzir acoplamento, permitir testes isolados e preparar o pipeline de transformação HL7v2 → FHIR.

### Implementado

- `src/gateway/core/hl7_parser.py`;
- `ParsedHL7Message` como representação interna previsível;
- normalização de quebras de segmento;
- parsing específico de `MSH-1` e `MSH-2`;
- uso do separador definido em `MSH-1` nos demais segmentos;
- `src/gateway/core/hl7_validator.py`;
- `ValidationResult` com `valid`, `ack_code`, `reason` e `errors`;
- Receiver refatorado para transporte/orquestração;
- suíte automatizada em `tests/gateway/test_hl7_core.py`.

### Matriz validada

```text
ADT^A01 válido          -> AA -> PASS
ADT^A01 sem MSH-10      -> AE -> PASS
ORM^O01 não suportado   -> AR -> PASS
```

### Testes automatizados

```text
[x] ADT^A01 válido retorna AA
[x] MSH-10 ausente retorna AE
[x] ORM^O01 não suportado retorna AR
[x] segmentos MSH/EVN/PID/PV1 expostos pelo Parser
[x] mensagem vazia gera erro controlado
[x] mensagem sem MSH gera erro controlado

Ran 6 tests
OK
```

### Troubleshooting

Após o desacoplamento, a execução direta do arquivo:

```bash
python3 src/gateway/receivers/mllp_receiver.py
```

resultou em:

```text
ModuleNotFoundError: No module named 'src'
```

A causa foi o contexto de importação do Python ao executar um arquivo interno diretamente. A execução foi padronizada como módulo:

```bash
python3 -m src.gateway.receivers.mllp_receiver
```

Com isso, os imports absolutos do pacote `src` passaram a ser resolvidos corretamente.

### Known limitation

A estrutura atual armazena segmentos por nome em um dicionário. Segmentos repetidos, como múltiplos `OBX`, ainda não são preservados como coleção. Essa limitação não afeta o ADT^A01 atual e será tratada antes da evolução para ORM/ORU.

### Fluxo implementado após o Milestone 1.4

```text
HIS Simulator
      |
      | HL7v2 / MLLP
      v
MLLP Receiver
      |
      v
HL7 Parser
      |
      v
Validator Core
      |
      +--> AA / AE / AR
      |
      v
ACK via MLLP
```


---

## Milestone 1.5 — ADT^A01 → FHIR Patient + Encounter

### Objetivo

Transformar o conteúdo do `ADT^A01` em recursos FHIR R4, persistir `Patient` e `Encounter` no HAPI FHIR e conectar o fluxo MLLP ao destino FHIR.

### Implementado

- `src/gateway/transformers/adt_a01_to_fhir.py`;
- mapping `PID → Patient`;
- mapping `PV1 → Encounter`;
- rastreabilidade por `MSH-10` em `meta.source`;
- `src/gateway/clients/fhir_client.py`;
- criação de resources via REST FHIR;
- captura do ID retornado pelo servidor;
- `src/gateway/services/adt_a01_service.py`;
- vínculo real `Encounter.subject.reference = Patient/{id}`;
- integração do service ao MLLP Receiver;
- ACK `AA` após persistência bem-sucedida;
- ACK `AE` preparado para falhas no processamento/persistência;
- 8 testes automatizados consolidados.

### Validação end-to-end

```text
HIS Simulator
-> MLLP Receiver
-> HL7 Parser
-> Validator Core
-> ADT^A01 to FHIR Transformer
-> FHIR Client
-> HAPI FHIR
-> PostgreSQL
-> ACK AA
```

Execução validada:

```text
Patient/1057
Encounter/1058
Encounter.subject.reference = Patient/1057
ACK TYPE: AA
ACK VALIDATION RESULT: PASS
```

Os IDs acima representam uma execução local específica e servem apenas como evidência técnica.

### Testes

```text
Ran 8 tests in 0.004s
OK
```

---

## Próximo milestone

### Milestone 1.6 — End-to-end hardening e confiabilidade

Prioridades:

1. idempotência e prevenção de duplicidade;
2. testes automatizados do FHIR Client e do service;
3. comportamento controlado com FHIR Server indisponível;
4. logs e auditoria estruturados;
5. tratamento de erros/retry;
6. maior rigor na validação FHIR;
7. melhoria da semântica temporal;
8. preparação para expansão do gateway.

O fluxo funcional principal do MVP já está conectado ponta a ponta. O próximo milestone deixa de ser integração básica e passa a focar confiabilidade operacional.
