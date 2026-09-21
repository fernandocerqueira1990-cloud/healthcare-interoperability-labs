# Milestone 1.5 — ADT^A01 → FHIR Patient + Encounter

## 1. Contexto

Após os milestones de ambiente FHIR, HIS Simulator, transporte MLLP, parsing e validação, o Milestone 1.5 conectou o conteúdo clínico-administrativo do `ADT^A01` ao modelo FHIR R4.

O objetivo foi transformar dados dos segmentos `PID` e `PV1` em recursos `Patient` e `Encounter`, persistir ambos no HAPI FHIR e preservar o vínculo entre atendimento e paciente.

## 2. Fluxo implementado

```text
HIS Simulator
      |
      | HL7v2 ADT^A01 / TCP / MLLP
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
ADT^A01 -> FHIR Transformer
      |
      +--> Patient
      |
      +--> Encounter
      |
      v
FHIR Client
      |
      | REST / application/fhir+json
      v
HAPI FHIR R4
      |
      v
PostgreSQL
      |
      v
ACK AA
```

## 3. Componentes implementados

### Transformer

Arquivo:

```text
src/gateway/transformers/adt_a01_to_fhir.py
```

Responsabilidades:

- mapear `PID` para `Patient`;
- mapear `PV1` para `Encounter`;
- normalizar data HL7 `YYYYMMDD` para FHIR `YYYY-MM-DD`;
- mapear sexo administrativo para `Patient.gender`;
- mapear `PV1-2` para `Encounter.class`;
- preservar rastreabilidade por `meta.source`;
- permitir que o `Encounter` receba uma referência real de `Patient`.

### FHIR Client

Arquivo:

```text
src/gateway/clients/fhir_client.py
```

Responsabilidades:

- serializar resources em JSON;
- executar `POST` no endpoint do tipo de recurso;
- usar `application/fhir+json`;
- capturar status HTTP;
- capturar o `id` do recurso criado;
- tratar `HTTPError` e `URLError`.

### ADT A01 Service

Arquivo:

```text
src/gateway/services/adt_a01_service.py
```

Responsabilidades:

1. receber HL7 bruto;
2. executar parsing;
3. validar a mensagem;
4. construir `Patient`;
5. persistir `Patient`;
6. capturar o ID FHIR real;
7. construir `Encounter` com `subject.reference = Patient/{id}`;
8. persistir `Encounter`;
9. retornar os IDs persistidos.

## 4. Mapping implementado

### PID → Patient

| HL7v2 | FHIR R4 |
|---|---|
| `PID-3` | `Patient.identifier` |
| `PID-5` | `Patient.name` |
| `PID-7` | `Patient.birthDate` |
| `PID-8` | `Patient.gender` |
| `PID-11` | `Patient.address` |
| `PID-13` | `Patient.telecom` |
| `MSH-10` | `Patient.meta.source` para rastreabilidade |

### PV1 → Encounter

| HL7v2 | FHIR R4 |
|---|---|
| `PV1-19` | `Encounter.identifier` |
| `PV1-2` | `Encounter.class` |
| `PV1-3` | `Encounter.location.location.display` |
| `PV1-44` | `Encounter.period.start` |
| ID do Patient persistido | `Encounter.subject.reference` |
| `MSH-10` | `Encounter.meta.source` para rastreabilidade |

## 5. Decisões técnicas

### Não inventar timezone

A mensagem sintética contém `PV1-44 = 20260914231500`, mas não contém offset de timezone.

Para evitar inserir semântica não presente na origem, o milestone preserva apenas a data:

```text
20260914231500 -> 2026-09-14
```

Uma evolução futura poderá transportar timezone explícito e preservar o timestamp completo.

### Referência real entre resources

Durante o desenvolvimento inicial foi usada a referência temporária:

```text
Patient/temporary
```

Após validar a criação do `Patient`, o fluxo foi evoluído para capturar o ID retornado pelo HAPI FHIR e gerar:

```text
Encounter.subject.reference = Patient/{id-real}
```

No teste end-to-end documentado, o vínculo foi:

```text
Patient/1057
Encounter/1058
Encounter.subject.reference = Patient/1057
```

Esses IDs são evidências de uma execução local específica e não fazem parte da lógica fixa do sistema.

## 6. Testes automatizados

Foi criada a suíte:

```text
tests/gateway/test_adt_a01_to_fhir.py
```

Cobertura adicionada:

- transformação de ADT^A01 válido em `Patient`;
- transformação em `Encounter`;
- identifier do paciente;
- nome;
- gênero;
- data de nascimento;
- endereço;
- identifier do Encounter;
- status;
- class;
- referência ao paciente;
- período;
- localização;
- rastreabilidade via `MSH-10`.

Execução consolidada:

```bash
python3 -m unittest discover -s tests -v
```

Resultado observado:

```text
Ran 8 tests in 0.004s

OK
```

## 7. Integração com o MLLP Receiver

O `MLLP Receiver` passou a acionar o service após uma validação bem-sucedida.

Comportamento de sucesso:

```text
ADT^A01 válido
  -> persist Patient
  -> persist Encounter
  -> ACK AA
```

Comportamento de falha de persistência:

```text
ADT^A01 estruturalmente válido
  -> falha FHIR
  -> ACK AE
```

Isso faz o ACK refletir o resultado do processamento do gateway, e não apenas a validade sintática inicial da mensagem.

## 8. Validação manual

O fluxo foi validado em duas etapas.

Primeiro, criação manual via REST:

```text
POST /fhir/Patient   -> HTTP 201
POST /fhir/Encounter -> HTTP 201
```

Depois, execução end-to-end pelo HIS Simulator via MLLP.

Resultado no cliente:

```text
ACK TYPE: AA - Application Accept
ACK VALIDATION RESULT: PASS
```

Resultado no gateway:

```text
HL7 received | type=ADT^A01 | control_id=MSG00001
FHIR persistence completed | patient_id=1057 | encounter_id=1058 | correlation_id=MSG00001
ACK generated | code=AA | correlation_id=MSG00001
```

## 9. Validação dos resources persistidos

Consultas:

```bash
curl -s http://localhost:8080/fhir/Patient/1057 | python3 -m json.tool
curl -s http://localhost:8080/fhir/Encounter/1058 | python3 -m json.tool
```

Foi confirmado:

```text
Patient.identifier = 789012
Encounter.identifier = VN00001
Encounter.status = in-progress
Encounter.class.code = IMP
Encounter.period.start = 2026-09-14
Encounter.location = WARD / 101 / A
Encounter.subject.reference = Patient/1057
```

## 10. Resultado

O Milestone 1.5 está concluído e validado.

O projeto agora demonstra um fluxo real de interoperabilidade:

```text
HL7v2 ADT^A01
-> MLLP
-> parsing
-> validação
-> transformação FHIR R4
-> persistência REST
-> relacionamento Patient/Encounter
-> PostgreSQL
-> ACK
```

## 11. Próximo passo

Milestone 1.6 — endurecimento do pipeline end-to-end.

Focos previstos:

- idempotência e prevenção de duplicidade;
- testes automatizados do service e do FHIR client;
- comportamento controlado quando o FHIR Server estiver indisponível;
- validação explícita de respostas FHIR;
- logs/auditoria estruturados;
- melhoria do tratamento temporal;
- preparação do fluxo para novos tipos de mensagem.
