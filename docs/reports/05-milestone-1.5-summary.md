# Relatório Técnico — Milestone 1.5

## ADT^A01 → FHIR Patient + Encounter

### Status

**Concluído e validado.**

## Objetivo

Implementar a transformação HL7v2 → FHIR R4 e conectar o fluxo MLLP ao HAPI FHIR, criando `Patient` e `Encounter` relacionados.

## Resultado arquitetural

Antes:

```text
HIS Simulator
-> MLLP Receiver
-> Parser
-> Validator
-> ACK
```

Depois:

```text
HIS Simulator
-> MLLP Receiver
-> Parser
-> Validator
-> Transformer
-> FHIR Client
-> HAPI FHIR
-> PostgreSQL
-> ACK
```

## Entregas

- transformer `ADT^A01 -> Patient + Encounter`;
- mapping de `PID` para `Patient`;
- mapping de `PV1` para `Encounter`;
- rastreabilidade via `MSH-10`;
- FHIR Client para criação de resources;
- service de orquestração ADT^A01;
- captura do ID FHIR real do paciente;
- vínculo `Encounter.subject.reference`;
- integração do service ao MLLP Receiver;
- 2 novos testes automatizados de transformação;
- 8 testes totais passando;
- validação manual via REST;
- validação end-to-end via MLLP.

## Evidência principal

Execução ponta a ponta:

```text
HL7 received | type=ADT^A01 | control_id=MSG00001
FHIR persistence completed | patient_id=1057 | encounter_id=1058
ACK generated | code=AA | correlation_id=MSG00001
```

Cliente:

```text
ACK TYPE: AA - Application Accept
ACK VALIDATION RESULT: PASS
```

Persistência:

```text
Patient/1057
Encounter/1058
Encounter.subject.reference = Patient/1057
```

## Decisões de engenharia

- transformação isolada da camada de transporte;
- FHIR Client isolado da regra ADT;
- service responsável pela orquestração;
- não inserir timezone inexistente na origem;
- ACK `AA` somente após persistência FHIR bem-sucedida;
- falha de persistência convertida em `AE`;
- uso exclusivo de dados sintéticos no repositório público.

## Testes

```text
Ran 8 tests in 0.004s
OK
```

## Limitações conhecidas

- `POST` simples ainda permite duplicar resources em reenvios;
- idempotência ainda não foi implementada;
- service e FHIR Client ainda precisam de testes automatizados específicos;
- timestamp HL7 ainda não preserva timezone;
- segmentos repetidos continuam sendo uma limitação do parser atual;
- auditoria ainda é baseada em logs, sem persistência dedicada.

## Próximo milestone

**Milestone 1.6 — End-to-end hardening e confiabilidade do pipeline**

Prioridades:

1. idempotência;
2. controle de duplicidade;
3. testes do FHIR Client e service;
4. cenários de indisponibilidade do FHIR Server;
5. logs estruturados e auditoria;
6. validação mais rigorosa dos resources e respostas;
7. preparação para expansão do gateway.
