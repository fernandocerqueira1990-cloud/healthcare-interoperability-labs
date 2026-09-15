# Milestone 1.2 — HIS Simulator e HL7v2 ADT^A01

## Objetivo

Criar e validar uma mensagem HL7v2 sintética do tipo `ADT^A01`, representando a admissão de um paciente, como primeira etapa do HIS Simulator do Healthcare Integration Gateway.

Nesta fase ainda não há transporte MLLP. O foco é compreender a estrutura da mensagem, inspecionar campos, validar requisitos mínimos e preparar o pipeline para MLLP, ACK/NACK, parsing, transformação e roteamento.

## Fluxo atual

```text
Paciente admitido
      |
      v
HIS Simulator
      |
      v
HL7v2 ADT^A01
      |
      v
Inspeção de campos
      |
      v
Validação estrutural
```

## Conceito ADT^A01

`ADT` significa **Admission, Discharge and Transfer**. O evento `A01` representa uma admissão/visita de paciente.

Em um ambiente hospitalar, esse evento pode ser consumido por LIS, RIS, PACS, faturamento, data warehouse e plataformas de integração.

## Segmentos utilizados

### MSH — Message Header

Cabeçalho da mensagem. Campos relevantes usados no laboratório:

- `MSH-1` — Field Separator (`|`)
- `MSH-2` — Encoding Characters (`^~\\&`)
- `MSH-3` — Sending Application
- `MSH-4` — Sending Facility
- `MSH-5` — Receiving Application
- `MSH-6` — Receiving Facility
- `MSH-7` — Date/Time of Message
- `MSH-9` — Message Type (`ADT^A01`)
- `MSH-10` — Message Control ID
- `MSH-11` — Processing ID
- `MSH-12` — HL7 Version (`2.5`)

### EVN — Event Type

Representa informações do evento. Neste laboratório registra o evento `A01` e seu timestamp.

### PID — Patient Identification

Contém identificação e dados demográficos do paciente. Campos validados:

- `PID-3` — Patient Identifier List
- `PID-5` — Patient Name
- `PID-7` — Date of Birth
- `PID-8` — Administrative Sex
- `PID-11` — Patient Address
- `PID-13` — Phone Number

### PV1 — Patient Visit

Contém dados do atendimento/episódio. Campos importantes:

- `PV1-2` — Patient Class
- `PV1-3` — Assigned Patient Location
- `PV1-7` — Attending Doctor
- `PV1-19` — Visit Number
- `PV1-44` — Admit Date/Time

## Paciente x visita

O identificador do paciente e o número da visita representam conceitos diferentes. Um paciente pode ter múltiplos episódios ao longo do tempo.

```text
Patient
  |-- Visit 1
  |-- Visit 2
  `-- Visit 3
```

Essa distinção será importante na futura transformação HL7v2 → FHIR:

```text
PID -> Patient
PV1 -> Encounter
```

## Inspeção estrutural

Foi criado um utilitário Python para exibir somente os campos preenchidos de cada segmento.

Durante a implementação foi identificada uma particularidade importante: o `MSH` precisa de tratamento especial, porque o próprio caractere localizado após `MSH` define `MSH-1` (Field Separator). Um `split('|')` ingênuo desloca a numeração dos campos de MSH.

A ferramenta foi ajustada para interpretar corretamente:

```text
MSH-1: |
MSH-2: ^~\&
MSH-3: HIS_DEMO
...
MSH-9: ADT^A01
MSH-10: MSG00001
MSH-12: 2.5
```

## Validação estrutural

Foi implementado um validador mínimo para o fluxo `ADT^A01`.

Validações atuais:

- presença de `MSH`;
- presença de `EVN`;
- presença de `PID`;
- presença de `PV1`;
- `MSH-9` preenchido e igual a `ADT^A01`;
- `MSH-10` preenchido;
- `MSH-12` preenchido;
- `PID-3` preenchido;
- `PID-5` preenchido;
- `PV1-2` preenchido;
- `PV1-19` preenchido;
- `PV1-44` preenchido.

O happy path foi validado com:

```text
VALIDATION RESULT: PASS
```

## Troubleshooting 1 — posição incorreta do Visit Number

Durante a montagem inicial do segmento `PV1`, o `Visit Number` ficou em `PV1-18` em vez de `PV1-19`, e o timestamp de admissão ficou deslocado.

### Causa

Quantidade incorreta de delimitadores `|` antes dos campos.

### Correção

A linha PV1 foi ajustada até que a inspeção automatizada retornasse:

```text
PV1-19: VN00001
PV1-44: 20260914231500
```

### Aprendizado

Em HL7v2, campos vazios continuam ocupando posição. Remover ou adicionar delimitadores altera o significado semântico dos campos seguintes.

## Teste negativo controlado

Para comprovar que o validador detectava inconsistências, o conteúdo de `PV1-19` foi removido intencionalmente.

Resultado:

```text
[ERROR] PV1-19 (Visit Number) vazio ou ausente
VALIDATION RESULT: FAIL
```

Depois o arquivo original foi restaurado e a validação executada novamente:

```text
[OK] PV1-19 (Visit Number) = VN00001
VALIDATION RESULT: PASS
```

Esse ciclo estabeleceu o padrão do projeto:

```text
detectar -> isolar -> validar -> corrigir -> revalidar -> documentar
```

## Relação conceitual com InterSystems

O laboratório é vendor-neutral e não utiliza tecnologia InterSystems. Ainda assim, os conceitos se relacionam de forma útil para estudo:

| Healthcare Integration Gateway | InterSystems |
|---|---|
| Sistema de origem | sistema externo / TrakCare |
| Recepção MLLP (futuro) | Business Service |
| Processamento | Business Process |
| Roteamento | Routing Rule |
| Transformação | DTL |
| Envio | Business Operation |
| Pipeline completo | Production |
| Logs / rastreabilidade | Message Viewer / Visual Trace |

Essa relação é conceitual, não uma equivalência de implementação.

## Próximos passos

1. implementar transporte MLLP;
2. gerar e interpretar ACK/NACK;
3. separar parser e validator como componentes independentes;
4. transformar `ADT^A01` em FHIR `Patient` + `Encounter`;
5. construir pipeline end-to-end;
6. adicionar observabilidade e auditoria.

## Pontos de estudo

Ao concluir esta etapa, deve ser possível explicar:

- o que é HL7v2;
- o que significam ADT e A01;
- o papel de MSH, EVN, PID e PV1;
- a diferença entre paciente e episódio;
- o que é Message Control ID;
- como funcionam os delimitadores HL7;
- por que MSH precisa de parsing especial;
- como um campo deslocado altera a semântica de uma mensagem;
- como uma validação estrutural detecta falhas;
- como PID/PV1 se relacionam conceitualmente com Patient/Encounter em FHIR;
- como o fluxo evoluirá para MLLP + ACK/NACK.
