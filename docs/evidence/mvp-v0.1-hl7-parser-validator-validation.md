# Evidência — MVP v0.1 / Milestone 1.4

## HL7 Parser + Validator Core

### Objetivo

Comprovar que o parsing e a validação HL7 foram desacoplados do transporte MLLP sem regressão funcional.

## Evidência 1 — Parser

Mensagem utilizada:

```text
src/his-simulator/messages/adt_a01.hl7
```

Resultado observado:

```text
Message Type       : ADT^A01
Trigger Event      : A01
Message Control ID : MSG00001
Processing ID      : P
Version ID         : 2.5
Segments           : ['MSH', 'EVN', 'PID', 'PV1']
```

Interpretação: o Parser extrai corretamente metadados e segmentos necessários ao fluxo atual.

## Evidência 2 — Validator / happy path

```text
Message Type : ADT^A01
Control ID   : MSG00001
Valid        : True
ACK Code     : AA
Reason       : Message accepted
Errors       : []
```

Resultado: PASS.

## Evidência 3 — Validator / AE

Entrada:

```text
ADT^A01 com MSH-10 ausente
```

Resultado:

```text
Message Type : ADT^A01
Control ID   : <missing>
Valid        : False
ACK Code     : AE
Reason       : HL7 validation failed
Errors:
  - Missing required field: MSH-10 (Message Control ID)
```

Resultado: PASS.

## Evidência 4 — Validator / AR

Entrada:

```text
ORM^O01
```

Resultado:

```text
Message Type : ORM^O01
Control ID   : MSG00002
Valid        : False
ACK Code     : AR
Reason       : Unsupported message type
Errors       : ['Unsupported message type: ORM^O01']
```

Resultado: PASS.

## Evidência 5 — Ponta a ponta MLLP

### AA

```text
HL7 received | type=ADT^A01 | control_id=MSG00001
ACK generated | code=AA | correlation_id=MSG00001
```

Cliente:

```text
ACK TYPE: AA - Application Accept
ACK VALIDATION RESULT: PASS
```

### AE

```text
HL7 received | type=ADT^A01 | control_id=<missing>
HL7 validation error | Missing required field: MSH-10 (Message Control ID)
ACK generated | code=AE | correlation_id=<missing>
```

Cliente:

```text
ACK TYPE: AE - Application Error
ACK VALIDATION RESULT: PASS
```

### AR

```text
HL7 received | type=ORM^O01 | control_id=MSG00002
HL7 validation error | Unsupported message type: ORM^O01
ACK generated | code=AR | correlation_id=MSG00002
```

Cliente:

```text
ACK TYPE: AR - Application Reject
ACK VALIDATION RESULT: PASS
```

## Evidência 6 — Testes automatizados

Comando:

```bash
python3 -m unittest tests.gateway.test_hl7_core -v
```

Resultado:

```text
test_empty_message_raises_error ... ok
test_message_without_msh_raises_error ... ok
test_missing_control_id_returns_ae ... ok
test_parser_exposes_expected_segments ... ok
test_unsupported_message_returns_ar ... ok
test_valid_adt_a01_returns_aa ... ok

Ran 6 tests in 0.002s

OK
```

## Evidência 7 — Validação de sintaxe

```bash
python3 -m py_compile \
src/gateway/core/hl7_parser.py \
src/gateway/core/hl7_validator.py \
src/gateway/receivers/mllp_receiver.py \
tests/gateway/test_hl7_core.py
```

Nenhum erro retornado.

## Troubleshooting registrado

A execução direta do Receiver passou a falhar com:

```text
ModuleNotFoundError: No module named 'src'
```

Forma padronizada:

```bash
python3 -m src.gateway.receivers.mllp_receiver
```

Resultado: Receiver iniciado normalmente em `127.0.0.1:2575`.

## Conclusão

O Milestone 1.4 foi validado com sucesso. O comportamento externo de ACK foi preservado enquanto parsing e validação foram movidos para componentes reutilizáveis e testáveis.
