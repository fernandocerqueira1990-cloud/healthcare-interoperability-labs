# Evidências — Milestone 1.3 MLLP + ACK/NACK

## Cenários validados

| Cenário | Entrada | Resultado |
|---|---|---|
| Happy Path | `ADT^A01` / `MSG00001` | ✅ `AA` |
| Application Error | `ADT^A01` / `MSH-10` vazio | ✅ `AE` |
| Application Reject | `ORM^O01` / `MSG00002` | ✅ `AR` |

## Resultado geral

```text
AA -> PASS
AE -> PASS
AR -> PASS
```

Todos os testes utilizaram dados sintéticos.

---

## Evidências técnicas

Foram confirmados em execução local:

- abertura do MLLP Receiver em `127.0.0.1:2575`;
- conexão do HIS Simulator;
- transporte TCP com framing MLLP;
- recepção de `ADT^A01`;
- retorno de ACK HL7v2;
- correlação por `Message Control ID`;
- tratamento de erro com `AE`;
- rejeição de tipo de mensagem não suportado com `AR`;
- logs do Receiver para conexão, mensagem e ACK.

---

## Evidência 1 — AA / Application Accept

Entrada:

```text
MSH-9  = ADT^A01
MSH-10 = MSG00001
```

Resposta observada:

```text
MSA|AA|MSG00001|Message accepted
ACK TYPE: AA - Application Accept
ACK VALIDATION RESULT: PASS
```

Log observado no Receiver:

```text
HL7 received | type=ADT^A01 | control_id=MSG00001
ACK generated | code=AA | correlation_id=MSG00001
```

---

## Evidência 2 — AE / Application Error

Entrada:

```text
MSH-9  = ADT^A01
MSH-10 = vazio
```

Resposta observada:

```text
MSA|AE||Missing Message Control ID
ACK TYPE: AE - Application Error
ACK VALIDATION RESULT: PASS
```

Log observado no Receiver:

```text
HL7 received | type=ADT^A01 | control_id=<missing>
HL7 validation failed | reason=missing MSH-10
ACK generated | code=AE | correlation_id=<missing>
```

---

## Evidência 3 — AR / Application Reject

Entrada:

```text
MSH-9  = ORM^O01
MSH-10 = MSG00002
```

Resposta observada:

```text
MSA|AR|MSG00002|Unsupported message type
ACK TYPE: AR - Application Reject
ACK VALIDATION RESULT: PASS
```

Log observado no Receiver:

```text
HL7 received | type=ORM^O01 | control_id=MSG00002
HL7 rejected | reason=unsupported message type | type=ORM^O01
ACK generated | code=AR | correlation_id=MSG00002
```

---

## Troubleshooting observado

Durante o teste `AE`, um delimitador `|` adicional no segmento `MSH` deslocou os campos `MSH-9` e `MSH-10`.

Sintoma inicial:

```text
type=
control_id=ADT^A01
```

A inspeção por índice demonstrou que `ADT^A01` havia sido deslocado para a posição correspondente a `MSH-10`.

Após correção do segmento `MSH`, o Receiver passou a interpretar:

```text
type=ADT^A01
control_id=<missing>
```

E o teste retornou corretamente:

```text
ACK TYPE: AE - Application Error
ACK VALIDATION RESULT: PASS
```

---

## Conclusão

O transporte MLLP e a geração de ACKs foram validados em três cenários controlados. O resultado comprova que o gateway já consegue receber mensagens HL7v2 por TCP/MLLP, correlacionar a resposta ao `MSH-10` quando disponível e diferenciar aceitação, erro e rejeição.
