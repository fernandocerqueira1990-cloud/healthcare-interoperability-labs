# Evidência — MVP v0.1 / Milestone 1.5

## ADT^A01 → FHIR Patient + Encounter — validação end-to-end

### Status

**PASS — fluxo validado de ponta a ponta.**

## Ambiente

- HAPI FHIR R4 `8.10.0`;
- PostgreSQL `16-alpine`;
- Docker Compose;
- MLLP Receiver em `127.0.0.1:2575`;
- HIS Simulator;
- Python 3;
- mensagem sintética `ADT^A01`.

## Pré-validação do ambiente

```bash
docker compose ps
```

Resultado observado:

```text
healthcare-hapi-fhir   Up
healthcare-postgres    Up (healthy)
```

O endpoint FHIR também foi validado:

```bash
curl http://localhost:8080/fhir/metadata
```

Resultado: `CapabilityStatement` retornado pelo HAPI FHIR.

## Testes automatizados

```bash
python3 -m unittest discover -s tests -v
```

Resultado:

```text
Ran 8 tests in 0.004s

OK
```

## Execução end-to-end

### Terminal 1 — Gateway

```bash
python3 -m src.gateway.receivers.mllp_receiver
```

Logs observados:

```text
Starting MLLP Receiver on 127.0.0.1:2575
MLLP Receiver listening on 127.0.0.1:2575
Connection opened
HL7 received | type=ADT^A01 | control_id=MSG00001
FHIR persistence completed | patient_id=1057 | encounter_id=1058 | correlation_id=MSG00001
ACK generated | code=AA | correlation_id=MSG00001
Connection closed
```

### Terminal 2 — HIS Simulator

```bash
python3 src/his-simulator/tools/send_mllp.py
```

Resultado:

```text
ACK received
MSA|AA|MSG00001|Message accepted

ACK TYPE: AA - Application Accept
ACK VALIDATION RESULT: PASS
```

## Resources criados

Execução validada:

```text
Patient/1057
Encounter/1058
```

### Patient

Consulta:

```bash
curl -s http://localhost:8080/fhir/Patient/1057 | python3 -m json.tool
```

Campos confirmados:

```text
resourceType = Patient
id = 1057
identifier.value = 789012
name.family = SANTOS
name.given[0] = MARINA
gender = female
birthDate = 1992-08-10
city = SALVADOR
state = BA
postalCode = 40000000
country = BRA
```

### Encounter

Consulta:

```bash
curl -s http://localhost:8080/fhir/Encounter/1058 | python3 -m json.tool
```

Campos confirmados:

```text
resourceType = Encounter
id = 1058
identifier.value = VN00001
status = in-progress
class.code = IMP
period.start = 2026-09-14
location.display = WARD / 101 / A
subject.reference = Patient/1057
```

## Critérios de aceite

```text
[x] mensagem ADT^A01 enviada pelo HIS Simulator
[x] transporte TCP/MLLP validado
[x] Parser executado
[x] Validator Core executado
[x] PID transformado em Patient
[x] PV1 transformado em Encounter
[x] Patient persistido no HAPI FHIR
[x] ID FHIR real capturado
[x] Encounter persistido com referência ao Patient
[x] ambos os resources recuperados pela API FHIR
[x] PostgreSQL saudável
[x] ACK AA retornado ao emissor
[x] correlação por MSH-10 preservada
[x] 8 testes automatizados passando
```

## Conclusão

O Healthcare Integration Gateway demonstrou, em ambiente local e com dados sintéticos, o primeiro fluxo completo de interoperabilidade do projeto.

A mensagem `ADT^A01` percorreu transporte, parsing, validação, transformação e persistência FHIR e retornou `AA` ao sistema emissor após o processamento bem-sucedido.
