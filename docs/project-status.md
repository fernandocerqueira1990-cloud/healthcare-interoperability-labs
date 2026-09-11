# Status do Projeto — Healthcare Integration Gateway

## Situação atual

O projeto está na fase **MVP v0.1**.

O **Milestone 1.1 — Ambiente FHIR Local** foi concluído e validado.

---

## Milestone 1.1 — Ambiente FHIR Local

### Objetivo

Criar um destino FHIR local, persistente e reproduzível antes de implementar o pipeline HL7v2 → FHIR.

### Componentes implementados

- HAPI FHIR R4 `8.10.0`;
- PostgreSQL `16-alpine`;
- Docker Compose;
- rede interna entre containers;
- volume persistente;
- configuração JDBC HAPI FHIR → PostgreSQL.

### Validações executadas

```text
[x] PostgreSQL saudável
[x] HAPI FHIR em execução
[x] CapabilityStatement retornado por /fhir/metadata
[x] HTTP 200 no endpoint de metadata
[x] Patient sintético criado via REST
[x] HTTP 201 na criação do Patient
[x] Patient recuperado por identifier
[x] Bundle searchset com total = 1
[x] Persistência comprovada após docker compose down/up
```

### Resultado técnico

A infraestrutura local foi validada ponta a ponta:

```text
Cliente REST
    |
    v
HAPI FHIR R4
    |
    | JDBC
    v
PostgreSQL
    |
    v
Docker Volume
```

O teste de persistência confirmou que o recurso `Patient` permaneceu disponível mesmo após remover e recriar os containers.

---

## Evidências funcionais principais

### Infraestrutura

```bash
docker compose ps
```

Resultado esperado e validado:

- `healthcare-hapi-fhir` ativo;
- `healthcare-postgres` ativo;
- PostgreSQL `healthy`;
- HAPI publicado em `localhost:8080`.

### Servidor FHIR

```bash
curl -s http://localhost:8080/fhir/metadata
```

Validado:

- `resourceType: CapabilityStatement`;
- HAPI FHIR Server `8.10.0`;
- FHIR `4.0.1 / R4`;
- HTTP `200`.

### Criação de recurso

Foi criado um `Patient` sintético por:

```text
POST /fhir/Patient
```

Validado:

```text
HTTP 201
resourceType: Patient
versionId: 1
```

### Busca por identificador de negócio

```bash
curl -s "http://localhost:8080/fhir/Patient?identifier=<MRN>"
```

Validado:

```text
resourceType: Bundle
type: searchset
total: 1
```

---

## Decisões arquiteturais já adotadas

- começar pelo destino FHIR antes do pipeline HL7v2;
- trabalhar com componentes separados e de baixo acoplamento;
- usar versão fixa das imagens para reprodutibilidade;
- manter PostgreSQL não exposto desnecessariamente ao host;
- persistir dados em Docker Volume;
- utilizar somente dados sintéticos no repositório público;
- documentar teoria, implementação, teste e troubleshooting junto com o código;
- preparar a arquitetura para futura configuração por cliente.

---

## Próximo milestone

### Milestone 1.2 — HL7v2 ADT^A01 + HIS Simulator

Objetivos previstos:

1. estudar a estrutura da mensagem ADT^A01;
2. documentar MSH, EVN, PID e PV1;
3. criar mensagens HL7v2 sintéticas;
4. implementar um HIS Simulator;
5. preparar o envio futuro por MLLP;
6. iniciar a associação entre campos HL7v2 e recursos FHIR `Patient` / `Encounter`.

Fluxo planejado:

```text
HIS Simulator
      |
      v
HL7v2 ADT^A01
      |
      v
MLLP Receiver
      |
      v
Parser
      |
      v
Validator
      |
      v
Transformer
      |
      v
FHIR Patient + Encounter
```

---

## Evolução prevista

```text
LAB
 |
 v
PoC
 |
 v
MVP
 |
 v
Piloto
 |
 v
Produto
```

O foco permanece em construir uma solução tecnicamente sólida, explicável, reproduzível e progressivamente aplicável a cenários reais de Healthcare IT.
