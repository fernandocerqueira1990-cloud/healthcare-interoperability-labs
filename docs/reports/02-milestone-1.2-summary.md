# Milestone 1.2 — HIS Simulator + HL7v2 ADT^A01

## Resumo executivo

Este milestone introduziu o sistema de origem do Healthcare Integration Gateway por meio de uma mensagem HL7v2 sintética `ADT^A01` e implementou ferramentas básicas de inspeção e validação estrutural.

A etapa consolidou conceitos fundamentais de interoperabilidade clínica antes da entrada de transporte MLLP e ACK/NACK.

## Entregas

- estrutura `src/his-simulator/`;
- mensagem HL7v2 `ADT^A01` sintética;
- segmentos `MSH`, `EVN`, `PID` e `PV1`;
- utilitário de inspeção de campos;
- tratamento correto da particularidade do segmento `MSH`;
- validador estrutural mínimo;
- happy path com `PASS`;
- teste negativo com remoção de `PV1-19`;
- detecção do erro com `FAIL`;
- restauração e revalidação com `PASS`;
- troubleshooting documentado para deslocamento de `PV1-19` / `PV1-44`;
- documentação conceitual e relação futura com FHIR e InterSystems.

## Principais conceitos técnicos

### HL7v2

Padrão amplamente utilizado para troca de mensagens clínicas e administrativas entre sistemas de saúde.

### ADT^A01

- `ADT`: Admission, Discharge and Transfer.
- `A01`: evento de admissão/visit notification.

### Segmentos

- `MSH`: Message Header.
- `EVN`: Event Type.
- `PID`: Patient Identification.
- `PV1`: Patient Visit.

### Identificadores

- `PID-3`: identificador do paciente/prontuário.
- `PV1-19`: identificador da visita/episódio.
- `MSH-10`: Message Control ID para rastreabilidade/correlação.

## Validação positiva

A mensagem completa passou por inspeção e validação mínima:

```text
VALIDATION RESULT: PASS
```

## Teste negativo

O `Visit Number` foi removido propositalmente de `PV1-19`.

Resultado:

```text
[ERROR] PV1-19 (Visit Number) vazio ou ausente
VALIDATION RESULT: FAIL
```

Após restauração:

```text
VALIDATION RESULT: PASS
```

## Troubleshooting

Na versão inicial da mensagem, `Visit Number` estava em `PV1-18` e a data/hora de admissão estava deslocada. A causa foi a quantidade incorreta de delimitadores de campos vazios.

A inspeção automatizada foi utilizada como evidência após a correção:

```text
PV1-19: VN00001
PV1-44: 20260914231500
```

## Padrão operacional consolidado

```text
detectar -> isolar -> validar -> corrigir -> revalidar -> documentar
```

## Relação com FHIR

A etapa prepara a futura transformação:

```text
PID -> FHIR Patient
PV1 -> FHIR Encounter
```

## Relação conceitual com InterSystems

O laboratório permanece vendor-neutral, mas os conceitos podem ser associados para fins de estudo:

- recepção MLLP → Business Service;
- processamento → Business Process;
- roteamento → Routing Rule;
- transformação → DTL;
- envio → Business Operation;
- pipeline → Production;
- rastreabilidade → Message Viewer / Visual Trace.

## Próxima etapa

**Milestone 1.3 — MLLP + ACK/NACK**.

Objetivo: transportar a mensagem, receber/processar o framing MLLP e responder com confirmação ou erro correlacionado à mensagem original.
