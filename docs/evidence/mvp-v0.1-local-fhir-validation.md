# Evidência — MVP v0.1 / Ambiente FHIR Local

## Objetivo

Registrar as validações executadas no ambiente local do Healthcare Integration Gateway para comprovar a disponibilidade do HAPI FHIR R4 e do PostgreSQL executados via Docker Compose.

## Data da validação

2026-09-11

## Ambiente

- Windows + WSL2 (Debian)
- Docker Desktop com integração WSL
- Docker Compose
- HAPI FHIR `v8.10.0-3`
- PostgreSQL `16-alpine`
- FHIR R4

## Validação 1 — Containers

Comando executado:

```bash
docker compose ps
```

Resultado observado:

- `healthcare-postgres`: em execução e `healthy`;
- `healthcare-hapi-fhir`: em execução;
- porta `8080` do HAPI publicada no host.

Conclusão: a infraestrutura containerizada iniciou corretamente.

## Validação 2 — Inicialização do PostgreSQL

Os logs confirmaram:

```text
database system is ready to accept connections
```

Também foi confirmada a criação do banco configurado para o HAPI FHIR.

Conclusão: o PostgreSQL está operacional e disponível para a aplicação.

## Validação 3 — Inicialização do HAPI FHIR

Os logs do HAPI mostraram a inicialização do servidor REST em modo FHIR R4 e a conclusão do startup da aplicação.

Trechos relevantes observados:

```text
Initializing HAPI FHIR restful server running in R4 mode
Tomcat started on port 8080 (http)
Started Application
```

Conclusão: o servidor FHIR foi inicializado corretamente.

## Validação 4 — CapabilityStatement

Endpoint acessado:

```text
http://localhost:8080/fhir/metadata
```

Também foi executado:

```bash
curl -s http://localhost:8080/fhir/metadata | head -n 30
```

Resultado observado:

```json
{
  "resourceType": "CapabilityStatement",
  "status": "active",
  "software": {
    "name": "HAPI FHIR Server",
    "version": "8.10.0"
  },
  "implementation": {
    "description": "HAPI FHIR R4 Server",
    "url": "http://localhost:8080/fhir"
  },
  "fhirVersion": "4.0.1"
}
```

No navegador, o servidor respondeu com:

```text
HTTP 200 OK
```

## O que esta validação comprova

A resposta `CapabilityStatement` confirma que:

- a aplicação está acessível via HTTP;
- o endpoint base FHIR está ativo;
- o servidor está operando em FHIR R4;
- a versão declarada é FHIR `4.0.1`;
- a API REST está pronta para receber operações FHIR.

## Status da etapa

```text
[x] PostgreSQL saudável
[x] HAPI FHIR em execução
[x] /fhir/metadata respondendo
[ ] Patient sintético criado
[ ] Patient recuperado via busca
[ ] Persistência após reinício
```

## Próximo teste

Criar um recurso `Patient` sintético por meio de um `POST /fhir/Patient` e validar o retorno HTTP `201 Created`.

> Nenhum dado real de paciente foi utilizado nesta validação.
