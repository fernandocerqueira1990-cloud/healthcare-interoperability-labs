# Milestone 1.4 — HL7 Parser + Validator Core

## 1. Contexto

O Milestone 1.3 comprovou o transporte HL7v2 sobre TCP/MLLP, framing, correlação por `MSH-10` e respostas `AA`, `AE` e `AR`. Porém, o `MLLP Receiver` ainda concentrava parsing e validação mínima.

O Milestone 1.4 remove esse acoplamento antes da implementação do Transformer HL7v2 → FHIR.

## 2. Problema de engenharia

Um componente de transporte não deve conhecer regras de parsing clínico nem validação de conteúdo. Manter tudo no Receiver aumenta acoplamento, dificulta testes unitários e torna futuras evoluções — como ORM, ORU, FHIR e outros transportes — mais arriscadas.

A decisão foi separar responsabilidades:

```text
MLLP Receiver
     |
     | raw HL7 payload
     v
HL7 Parser
     |
     | ParsedHL7Message
     v
Validator Core
     |
     | ValidationResult
     +------> ACK decision
     |
     v
Transformer (Milestone 1.5)
```

## 3. Componentes implementados

### 3.1 HL7 Parser

Arquivo:

```text
src/gateway/core/hl7_parser.py
```

Responsabilidades:

- normalizar quebras de segmento;
- identificar e interpretar segmentos;
- tratar `MSH` de forma especial;
- preservar `MSH-1` como field separator;
- usar o separador definido em `MSH-1` nos demais segmentos;
- extrair `MSH-9`, `MSH-10`, `MSH-11` e `MSH-12`;
- retornar uma representação interna previsível.

Contrato principal:

```text
raw HL7
   |
   v
parse_message()
   |
   v
ParsedHL7Message
```

O Parser não decide se a mensagem é aceita ou rejeitada.

### 3.2 ParsedHL7Message

A dataclass criada representa o resultado do parsing:

```text
ParsedHL7Message
- raw_message
- segments
- message_type
- trigger_event
- message_control_id
- processing_id
- version_id
```

Esse contrato reduz dependência entre transporte e validação.

### 3.3 Validator Core

Arquivo:

```text
src/gateway/core/hl7_validator.py
```

Responsabilidades:

- validar tipos de mensagem suportados;
- validar segmentos obrigatórios;
- validar campos obrigatórios;
- retornar resultado estruturado;
- orientar a decisão do ACK sem conhecer MLLP ou sockets.

Contrato:

```text
ValidationResult
- valid
- ack_code
- reason
- errors[]
```

### 3.4 MLLP Receiver

O Receiver foi refatorado para consumir:

```python
parse_message()
validate_message()
```

O parsing local de `MSH` foi removido.

O Receiver mantém responsabilidades de:

- socket TCP;
- framing MLLP;
- recepção e envio;
- orquestração do pipeline;
- construção e retorno do ACK;
- logs operacionais.

## 4. Regras atuais do ADT^A01

O fluxo atual suporta inicialmente `ADT^A01`.

Regras aplicadas:

- `MSH` obrigatório;
- `EVN` obrigatório;
- `PID` obrigatório;
- `PV1` obrigatório;
- `MSH-10` obrigatório;
- `MSH-12` obrigatório;
- `PID-3` obrigatório;
- `PID-5` obrigatório;
- `PV1-2` obrigatório;
- `PV1-19` obrigatório;
- `PV1-44` obrigatório.

## 5. Matriz de ACK validada

| Cenário | Resultado |
|---|---|
| ADT^A01 válido | `AA` |
| ADT^A01 sem `MSH-10` | `AE` |
| ORM^O01 não suportado | `AR` |

Os três cenários foram validados tanto no core quanto ponta a ponta via MLLP.

## 6. Testes automatizados

Arquivo:

```text
tests/gateway/test_hl7_core.py
```

Casos cobertos:

1. ADT^A01 válido retorna `AA`;
2. ausência de `MSH-10` retorna `AE`;
3. ORM^O01 retorna `AR`;
4. Parser expõe `MSH`, `EVN`, `PID` e `PV1`;
5. mensagem vazia gera erro controlado;
6. mensagem sem `MSH` gera erro controlado.

Execução:

```bash
python3 -m unittest tests.gateway.test_hl7_core -v
```

Resultado:

```text
Ran 6 tests in 0.002s

OK
```

## 7. Validação de sintaxe

```bash
python3 -m py_compile \
src/gateway/core/hl7_parser.py \
src/gateway/core/hl7_validator.py \
src/gateway/receivers/mllp_receiver.py \
tests/gateway/test_hl7_core.py
```

Resultado: nenhum erro.

## 8. Troubleshooting — ModuleNotFoundError

Após a criação do pacote `src.gateway.core`, executar diretamente:

```bash
python3 src/gateway/receivers/mllp_receiver.py
```

gerou:

```text
ModuleNotFoundError: No module named 'src'
```

A causa foi o contexto de importação criado pela execução direta de um arquivo interno.

A execução foi padronizada como módulo:

```bash
python3 -m src.gateway.receivers.mllp_receiver
```

Essa forma preserva a raiz do projeto no contexto de imports e é a forma recomendada para o Gateway neste estágio.

## 9. Decisões e boas práticas

- Single Responsibility Principle;
- baixo acoplamento entre transporte e core;
- contratos explícitos por dataclasses;
- testes unitários independentes de rede;
- regressão validada também ponta a ponta;
- propagação do field separator a partir de `MSH-1`;
- evolução incremental antes da transformação FHIR;
- documentação da limitação conhecida antes de ampliar escopo.

## 10. Limitação conhecida

A estrutura atual utiliza o nome do segmento como chave no dicionário:

```text
segments[segment_name]
```

Portanto, segmentos repetidos não são preservados como coleção.

Isso não afeta o ADT^A01 usado no MVP atual, mas precisa ser tratado antes de suportar mensagens como ORU, nas quais múltiplos `OBX` são comuns.

## 11. Critério de conclusão

```text
[x] parsing removido do Receiver
[x] Parser reutilizável implementado
[x] Validator Core independente implementado
[x] MSH-1 respeitado como field separator
[x] AA / AE / AR preservados
[x] testes ponta a ponta sem regressão
[x] 6 testes automatizados passando
[x] execução como módulo documentada
[x] troubleshooting documentado
[x] limitação de segmentos repetidos registrada
```

## 12. Próximo passo

Milestone 1.5:

```text
ADT^A01
  |
  +--> PID -> FHIR Patient
  |
  +--> PV1 -> FHIR Encounter
```

A transformação deverá manter rastreabilidade entre mensagem HL7 de origem e resources FHIR produzidos.
