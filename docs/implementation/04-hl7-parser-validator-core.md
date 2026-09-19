# Milestone 1.4 — HL7 Parser + Validator Core

## 1. Contexto

Após o Milestone 1.3, o projeto já comprova transporte HL7v2 sobre TCP/MLLP, framing, correlação por `MSH-10` e geração de ACK `AA`, `AE` e `AR`. Entretanto, parte do parsing necessário para decidir o ACK ainda está dentro do `MLLP Receiver`.

O objetivo deste milestone é separar responsabilidades antes de iniciar a transformação HL7v2 → FHIR.

## 2. Problema de engenharia

Um Receiver de transporte não deve concentrar regras de parsing, validação clínica/estrutural e transformação. Esse acoplamento aumenta complexidade, dificulta testes unitários, reduz reutilização e faz mudanças em mensagens HL7 afetarem código de rede.

A decisão arquitetural é separar o pipeline em componentes com contratos claros:

```text
MLLP Receiver
     |
     | raw HL7 payload
     v
HL7 Parser
     |
     | parsed message model
     v
Validator Core
     |
     | validation result
     +------> ACK decision
     |
     v
Transformer (Milestone 1.5)
```

## 3. Responsabilidades

### MLLP Receiver

Responsável por:

- socket TCP;
- bind/listen/accept;
- framing MLLP;
- extração do payload HL7;
- envio do ACK pelo mesmo transporte;
- tratamento de erros de transporte.

Não deve conhecer detalhes de `PID`, `PV1`, `OBX` ou regras de transformação FHIR.

### HL7 Parser

Responsável por:

- normalizar quebras de segmento;
- separar segmentos e campos;
- tratar `MSH-1` e `MSH-2` corretamente;
- fornecer acesso consistente a campos HL7;
- extrair metadados como `MSH-9`, `MSH-10`, `MSH-11` e `MSH-12`;
- retornar erro controlado quando a estrutura mínima não puder ser interpretada.

O Parser **não decide** se uma mensagem é aceita pelo negócio. Ele apenas transforma texto HL7 em uma representação interna previsível.

### Validator Core

Responsável por:

- verificar tipo de mensagem suportado;
- validar presença de campos mínimos;
- validar segmentos esperados para o fluxo suportado;
- produzir resultado estruturado de validação;
- fornecer informação suficiente para a decisão `AA`, `AE` ou `AR`.

O Validator não deve abrir sockets nem enviar ACK diretamente.

## 4. Contratos propostos

### Entrada do Parser

```text
raw_message: str
```

### Saída conceitual do Parser

```text
ParsedHL7Message
- segments
- message_type
- trigger_event
- control_id
- processing_id
- version_id
```

### Saída conceitual do Validator

```text
ValidationResult
- valid: bool
- ack_code: AA | AE | AR
- reason
- errors[]
```

Os nomes finais podem evoluir durante a implementação, mas o contrato deve permanecer explícito e testável.

## 5. Regras iniciais do ADT^A01

Para o escopo atual:

- `MSH` obrigatório;
- `MSH-9` deve identificar `ADT^A01`;
- `MSH-10` obrigatório para correlação;
- `PID` obrigatório;
- `PV1` obrigatório para o cenário de admissão;
- mensagem estruturalmente inválida deve produzir erro controlado;
- tipo de mensagem não suportado deve produzir `AR`;
- erro de conteúdo/processamento deve produzir `AE`;
- mensagem suportada e válida deve produzir `AA`.

## 6. Estratégia de testes

A implementação só será considerada concluída depois dos seguintes cenários reproduzíveis:

| Cenário | Resultado esperado |
|---|---|
| ADT^A01 válido | Parser OK + Validator PASS + ACK AA |
| `MSH-10` ausente | Validation error + ACK AE |
| tipo `ORM^O01` no escopo atual | Unsupported + ACK AR |
| `PID` ausente | Validation error + ACK AE |
| `PV1` ausente | Validation error + ACK AE |
| payload sem `MSH` | Parse/validation failure controlada |

## 7. Boas práticas aplicadas

- **Single Responsibility Principle:** transporte, parsing e validação separados;
- **baixo acoplamento:** Parser e Validator não dependem do socket MLLP;
- **testabilidade:** regras podem ser testadas sem abrir porta TCP;
- **reutilização:** o mesmo Parser poderá ser usado por arquivos, filas ou APIs futuramente;
- **evolução incremental:** somente após estabilizar o modelo HL7 interno será iniciado o mapper para FHIR;
- **observabilidade:** erros devem preservar contexto suficiente para troubleshooting sem expor dados sensíveis desnecessários.

## 8. Critério de conclusão

O Milestone 1.4 estará concluído quando:

```text
[x] Receiver limitado à responsabilidade de transporte
[x] Parser HL7 reutilizável implementado
[x] Validator Core independente implementado
[x] ACK continua correlacionado pelo Message Control ID
[x] cenários AA / AE / AR continuam funcionando
[x] testes negativos documentados
[x] documentação e evidências atualizadas
[x] nenhuma regressão no Milestone 1.3
```

Os itens serão marcados somente após execução e evidência real.

## 9. Próximo milestone

Após a validação do Parser + Validator Core, o Milestone 1.5 implementará o primeiro mapeamento de interoperabilidade:

```text
ADT^A01
  |
  +--> PID -> FHIR Patient
  |
  +--> PV1 -> FHIR Encounter
```

A transformação deverá preservar rastreabilidade entre a mensagem HL7 de origem e os recursos FHIR produzidos.
