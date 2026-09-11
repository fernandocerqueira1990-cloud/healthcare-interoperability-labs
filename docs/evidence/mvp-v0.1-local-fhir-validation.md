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

## Validação 5 — Criação de Patient sintético

Foi executado um `POST /fhir/Patient` utilizando um recurso FHIR sintético.

Resultado observado:

```text
HTTP/1.1 201
```

O HAPI FHIR retornou o recurso persistido com:

```text
resourceType: Patient
id: 1000
versionId: 1
```

Também foi retornado o cabeçalho:

```text
Location: http://localhost:8080/fhir/Patient/1000/_history/1
```

### Interpretação

O código HTTP `201` confirma que o recurso foi criado com sucesso.

O `id` `1000` é o identificador lógico atribuído pelo servidor FHIR ao recurso.

O `versionId` `1` indica a primeira versão persistida desse recurso.

O cabeçalho `Location` aponta para a versão recém-criada no histórico do recurso.

Conclusão: o HAPI FHIR recebeu, validou e persistiu com sucesso um recurso `Patient` FHIR R4 no PostgreSQL.

## O que estas validações comprovam

As validações realizadas até aqui confirmam que:

- a aplicação está acessível via HTTP;
- o endpoint base FHIR está ativo;
- o servidor está operando em FHIR R4;
- a versão declarada é FHIR `4.0.1`;
- a API REST aceita operações de criação;
- um recurso `Patient` válido pode ser persistido;
- o HAPI FHIR está integrado ao PostgreSQL.

## Status da etapa

```text
[x] PostgreSQL saudável
[x] HAPI FHIR em execução
[x] /fhir/metadata respondendo
[x] Patient sintético criado
[ ] Patient recuperado via busca
[ ] Persistência após reinício
```

## Próximo teste

Pesquisar o `Patient` pelo identificador hospitalar sintético `123456` e validar que o servidor retorna um `Bundle` contendo o recurso criado.

> Nenhum dado real de paciente foi utilizado nesta validação.
