# Relatório Técnico — Milestone 1.1

## Healthcare Integration Gateway — Ambiente FHIR Local

Este relatório resume o que foi implementado, como foi implementado, por que cada decisão foi tomada e o que foi validado na primeira etapa executável do Healthcare Integration Gateway.

---

## 1. Contexto

O projeto nasceu a partir de laboratórios de interoperabilidade em saúde com HL7v2, FHIR, DICOM/DICOMweb e Google Cloud Healthcare API.

A evolução atual tem um objetivo adicional: transformar esse conhecimento em uma base própria, modular, reproduzível e preparada para evoluir de laboratório para PoC, MVP, piloto e produto.

---

## 2. Objetivo do Milestone 1.1

Antes de construir o pipeline HL7v2 → FHIR, foi criado e validado o destino FHIR.

A decisão de começar pelo destino reduz variáveis durante o desenvolvimento. Primeiro comprovamos que o servidor FHIR, a persistência e a API REST funcionam; depois adicionamos MLLP, parsing, validação e transformação.

Arquitetura implementada:

```text
Developer / Gateway
        |
        | HTTP REST :8080
        v
   HAPI FHIR R4
        |
        | JDBC :5432
        v
     PostgreSQL
        |
        v
   Docker Volume
```

---

## 3. Tecnologias

| Tecnologia | Função | Motivo |
|---|---|---|
| Docker | Executar serviços em containers | Isolamento e reprodutibilidade |
| Docker Compose | Orquestrar os serviços | Configuração declarativa do ambiente |
| HAPI FHIR 8.10.0 | Servidor FHIR R4 | API REST e persistência de recursos FHIR |
| PostgreSQL 16-alpine | Banco de dados | Persistência estruturada |
| Docker Volume | Persistência física | Manter dados fora do ciclo de vida dos containers |
| FHIR R4 / 4.0.1 | Padrão de interoperabilidade | Base do primeiro fluxo do MVP |
| WSL2 Debian | Ambiente Linux local | Desenvolvimento e execução dos testes |

---

## 4. Preparação do ambiente

O repositório foi clonado no Debian/WSL:

```bash
git clone https://github.com/fernandocerqueira1990-cloud/healthcare-interoperability-labs.git
cd healthcare-interoperability-labs
```

O Docker Desktop foi integrado ao WSL2 e validado com:

```bash
docker run hello-world
```

A mensagem `Hello from Docker!` confirmou comunicação entre Docker CLI e daemon, download de imagem e execução de container.

---

## 5. Infraestrutura Docker

Foram criados:

```text
docker/
├── docker-compose.yml
└── hapi.application.yaml
```

O ambiente contém dois serviços principais:

- `healthcare-hapi-fhir`;
- `healthcare-postgres`.

O HAPI acessa o PostgreSQL pelo nome interno do serviço Docker:

```text
jdbc:postgresql://db:5432/hapi
```

Isso evita o erro conceitual de usar `localhost` entre containers.

---

## 6. Rede interna

Os containers utilizam uma rede Docker dedicada.

Dentro de um container:

```text
localhost = o próprio container
```

Por isso o HAPI FHIR resolve o banco pelo hostname `db`, fornecido pelo DNS interno do Docker Compose.

---

## 7. Persistência

O PostgreSQL usa um volume Docker persistente.

```text
Container PostgreSQL
        |
        v
Docker Volume
        |
        v
Dados persistentes
```

Isso permite remover e recriar containers sem perder os recursos FHIR armazenados.

---

## 8. Health check

O PostgreSQL executa:

```bash
pg_isready -U admin -d hapi
```

O HAPI só inicia após o banco ser considerado saudável, evitando falhas por ordem incorreta de inicialização.

---

## 9. Subida do ambiente

```bash
cd docker
docker compose up -d
docker compose ps
```

Foi validado:

- HAPI FHIR em execução;
- PostgreSQL em execução;
- PostgreSQL `healthy`;
- porta `8080` publicada para o HAPI.

Os logs confirmaram:

```text
database system is ready to accept connections
Initializing HAPI FHIR restful server running in R4 mode
Tomcat started on port 8080
Started Application
```

---

## 10. CapabilityStatement

Endpoint:

```text
http://localhost:8080/fhir/metadata
```

Validações:

```text
HTTP 200 OK
resourceType: CapabilityStatement
software: HAPI FHIR Server 8.10.0
fhirVersion: 4.0.1
```

O `CapabilityStatement` funciona como uma declaração formal das capacidades do servidor FHIR.

---

## 11. Primeiro Patient FHIR

Foi criado um recurso sintético por REST:

```text
POST /fhir/Patient
Content-Type: application/fhir+json
```

Resultado:

```text
HTTP 201
resourceType: Patient
versionId: 1
```

O servidor também atribuiu um `id` lógico ao recurso e retornou o cabeçalho `Location`.

---

## 12. ID interno x identifier de negócio

Exemplo conceitual:

```text
FHIR internal id: Patient/1000
Business identifier / MRN: 123456
```

O `id` é controlado pelo servidor FHIR. O `identifier` representa um identificador de negócio conhecido pelos sistemas de origem, como MRN/prontuário.

---

## 13. Busca por identifier

Foi executada uma busca FHIR por identificador de negócio:

```bash
curl -s "http://localhost:8080/fhir/Patient?identifier=123456"
```

Resultado:

```text
resourceType: Bundle
type: searchset
total: 1
```

O recurso `Patient` foi recuperado sem depender do ID interno do servidor.

---

## 14. Teste de persistência

Os containers foram removidos e recriados:

```bash
docker compose down
docker compose up -d
```

Após o startup completo, a busca pelo mesmo identificador retornou novamente:

```text
total: 1
```

Isso comprovou que os dados permaneceram no PostgreSQL através do Docker Volume.

---

## 15. Checklist final

```text
[x] PostgreSQL saudável
[x] HAPI FHIR em execução
[x] /fhir/metadata respondendo
[x] CapabilityStatement validado
[x] Patient sintético criado
[x] HTTP 201 validado
[x] Patient recuperado por identifier
[x] Bundle searchset validado
[x] Persistência comprovada após reinício
```

---

## 16. Decisões arquiteturais

- começar pelo destino FHIR antes da origem HL7v2;
- separar aplicação e banco;
- usar versão fixa das imagens Docker;
- não expor o PostgreSQL ao host sem necessidade;
- usar rede interna Docker;
- manter dados em volume persistente;
- usar somente dados sintéticos;
- documentar implementação, validação e troubleshooting;
- manter a arquitetura preparada para baixo acoplamento e multi-cliente.

---

## 17. O que esta etapa comprova

O projeto já demonstra na prática:

- infraestrutura containerizada;
- HAPI FHIR R4 operacional;
- PostgreSQL integrado via JDBC;
- rede entre containers;
- API REST FHIR;
- criação de recurso clínico/administrativo;
- pesquisa FHIR;
- identificador de negócio;
- persistência de dados;
- validação pós-restart;
- documentação técnica reproduzível.

---

## 18. Próximo passo

**Milestone 1.2 — HL7v2 ADT^A01 + HIS Simulator**

```text
HIS Simulator
      |
      v
HL7v2 ADT^A01
      |
      v
MLLP
      |
      v
Parser -> Validator -> Transformer
      |
      v
FHIR Patient + Encounter
```

A próxima etapa começa pelo entendimento teórico de `MSH`, `EVN`, `PID` e `PV1`, seguido da criação das mensagens sintéticas e do simulador de origem.

---

## 19. Conclusão

O Milestone 1.1 foi concluído com sucesso. O Healthcare Integration Gateway já possui um destino FHIR local, persistente e reproduzível, validado por operações REST reais e preparado para receber progressivamente as demais camadas do pipeline de interoperabilidade.
