# Relatório Técnico — Milestone 1.4

## HL7 Parser + Validator Core desacoplados

### Status

**Concluído e validado.**

## Objetivo

Refatorar o Healthcare Integration Gateway para separar as responsabilidades de transporte MLLP, parsing HL7 e validação estrutural antes da implementação HL7v2 → FHIR.

## Resultado arquitetural

Antes:

```text
MLLP Receiver
├── transporte
├── parsing MSH
├── validação
└── decisão do ACK
```

Depois:

```text
MLLP Receiver
      |
      v
HL7 Parser
      |
      v
Validator Core
      |
      +--> AA / AE / AR
```

Essa alteração reduz acoplamento e cria uma base reutilizável para o Transformer FHIR.

## Entregas

- `src/gateway/core/hl7_parser.py`;
- `src/gateway/core/hl7_validator.py`;
- refatoração de `mllp_receiver.py`;
- `ParsedHL7Message`;
- `ValidationResult`;
- propagação do field separator a partir de `MSH-1`;
- suíte de regressão com 6 testes;
- preservação de AA / AE / AR ponta a ponta.

## Validações

| Teste | Resultado |
|---|---|
| ADT^A01 válido | AA / PASS |
| ADT^A01 sem MSH-10 | AE / PASS |
| ORM^O01 não suportado | AR / PASS |
| mensagem vazia | erro controlado / PASS |
| mensagem sem MSH | erro controlado / PASS |
| segmentos esperados | PASS |

Automação:

```text
Ran 6 tests
OK
```

## Troubleshooting relevante

Após modularização, a execução direta do Receiver não resolvia o pacote `src`.

Erro:

```text
ModuleNotFoundError: No module named 'src'
```

Padrão adotado:

```bash
python3 -m src.gateway.receivers.mllp_receiver
```

## Limitação conhecida

Segmentos repetidos ainda não são representados como coleção. Antes de suportar ORU/múltiplos OBX, o modelo interno será evoluído para preservar repetição e ordem de segmentos quando necessário.

## Decisão de engenharia

A transformação FHIR não foi antecipada neste milestone. Primeiro foi estabilizada a interface entre transporte, parsing e validação. Essa sequência reduz risco de transportar dívida técnica para a camada de mapeamento clínico.

## Próximo milestone

**Milestone 1.5 — ADT^A01 → FHIR Patient + Encounter**

Próximas entregas:

- mapping `PID -> Patient`;
- mapping `PV1 -> Encounter`;
- testes de transformação;
- validação FHIR R4;
- preparação do envio ao HAPI FHIR.
