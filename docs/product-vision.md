# Product Vision — Healthcare Integration Gateway

## 1. Visão geral

O **Healthcare Integration Gateway** é a evolução do projeto `healthcare-interoperability-labs` de um conjunto de laboratórios técnicos para um MVP modular de interoperabilidade em saúde.

A proposta é construir uma solução capaz de receber, validar, transformar, rotear, monitorar e auditar dados clínicos e administrativos entre sistemas distintos, utilizando padrões amplamente adotados no ecossistema de saúde, como HL7v2, FHIR e APIs REST.

O projeto continuará tendo caráter educacional e experimental, porém sua arquitetura será desenhada desde o início para permitir evolução para PoC, MVP, piloto e, futuramente, um produto utilizável em ambientes reais.

---

## 2. Problema que o projeto pretende resolver

Ambientes de saúde normalmente possuem múltiplos sistemas, como:

- HIS — Hospital Information System
- LIS — Laboratory Information System
- RIS — Radiology Information System
- PACS — Picture Archiving and Communication System
- ERP
- Sistemas de terceiros
- Plataformas de telemedicina
- Aplicações móveis
- Data lakes e plataformas analíticas

Esses sistemas nem sempre utilizam o mesmo padrão de comunicação. É comum encontrar integrações baseadas em:

- HL7v2
- MLLP
- FHIR
- REST APIs
- JSON
- XML
- DICOM / DICOMweb
- Integrações via banco de dados

O desafio central é permitir que sistemas heterogêneos troquem informações de forma confiável, rastreável e padronizada.

O Healthcare Integration Gateway atuará como uma camada intermediária entre sistemas de origem e destino.

```text
Sistema A
    |
    v
Healthcare Integration Gateway
    |
    v
Sistema B
```

---

## 3. Objetivo do produto

Criar uma plataforma modular de interoperabilidade em saúde capaz de:

1. Receber mensagens e dados de diferentes origens.
2. Interpretar e fazer parsing dos dados recebidos.
3. Validar estrutura, campos e regras mínimas.
4. Transformar dados entre formatos e padrões.
5. Rotear a informação para diferentes destinos.
6. Registrar auditoria e rastreabilidade do processamento.
7. Realizar retry e tratamento controlado de falhas.
8. Disponibilizar métricas e observabilidade operacional.
9. Permitir configuração por cliente sem alteração do core da aplicação.

---

## 4. Princípios arquiteturais

### 4.1 Modularidade

Cada responsabilidade do sistema deverá ser isolada em componentes específicos.

```text
Receiver
   |
Parser
   |
Validator
   |
Transformer
   |
Router
   |
Destination
```

Componentes de auditoria, logs e monitoramento acompanham o fluxo de forma transversal.

### 4.2 Baixo acoplamento

O transporte utilizado para receber uma mensagem não deve determinar como ela será transformada ou enviada ao destino.

Exemplo:

- hoje: MLLP -> HL7v2 -> FHIR
- amanhã: REST -> JSON -> FHIR

O core da plataforma deverá permitir evolução sem reescrita completa.

### 4.3 Configuração por cliente

Regras específicas de clientes devem preferencialmente ser mantidas em configuração, e não codificadas diretamente no core.

Exemplo conceitual:

```yaml
client:
  id: hospital_demo
  name: Hospital Demo

input:
  protocol: mllp
  port: 2575

hl7:
  version: "2.5"

accepted_messages:
  - ADT_A01

output:
  type: fhir
  version: R4

mapping:
  ADT_A01: adt_a01_to_patient_encounter

retry:
  attempts: 3

audit:
  enabled: true
```

### 4.4 Observabilidade desde o início

Toda mensagem deverá possuir rastreabilidade.

Campos conceituais mínimos:

```text
message_id
client_id
message_type
received_at
processed_at
status
processing_time
destination
response
error
retry_count
```

### 4.5 Segurança e privacidade

Durante a fase de desenvolvimento serão utilizados dados sintéticos.

A evolução para ambientes reais deverá considerar, entre outros pontos:

- autenticação
- autorização
- criptografia em trânsito
- criptografia em repouso
- segregação por cliente
- proteção de credenciais
- auditoria
- minimização de dados
- políticas de retenção
- requisitos legais e regulatórios aplicáveis

---

## 5. Arquitetura conceitual inicial

```text
                    SISTEMAS DE ORIGEM

                HIS        LIS        RIS
                 |          |          |
                 +----------+----------+
                            |
                          HL7v2
                            |
                           MLLP
                            |
                            v

              +-------------------------+
              | Healthcare Integration  |
              |        Gateway          |
              +------------+------------+
                           |
              +------------+-------------+
              |            |             |
              v            v             v
            Parser      Validator       Audit
              |
              v
          Transformer

         HL7v2 -> FHIR

              |
              v
            Router
              |
       +------+-------+
       |      |       |
       v      v       v
     FHIR    API    Queue
     Server  externa futura
```

---

## 6. MVP inicial — v0.1

O primeiro fluxo implementado será uma integração de admissão hospitalar.

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
Receiver
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
      |
      v
HAPI FHIR
```

### Funcionalidades mínimas do MVP

- Receber HL7v2 via MLLP.
- Suportar inicialmente ADT^A01.
- Interpretar segmentos MSH, EVN, PID e PV1.
- Validar campos mínimos obrigatórios.
- Transformar dados para FHIR R4.
- Criar recursos Patient e Encounter.
- Enviar recursos ao HAPI FHIR.
- Gerar ACK HL7.
- Registrar logs de processamento.
- Registrar auditoria básica.
- Implementar retry controlado.
- Registrar mensagens com erro para análise e possível reprocessamento.

---

## 7. Evolução planejada

### v0.1

HL7v2 ADT -> FHIR Patient / Encounter.

### v0.2

Suporte a ORM e ORU.

Recursos FHIR adicionais:

- Observation
- DiagnosticReport
- ServiceRequest

### v0.3

REST API Gateway e webhooks.

### v0.4

Dashboard operacional.

### v0.5

Configuração multi-cliente.

### v0.6

Observabilidade avançada.

Possíveis componentes:

- Prometheus
- Grafana
- OpenTelemetry

### v0.7

Fluxos DICOM / DICOMweb.

### v0.8

Rules Engine para roteamento e transformação configurável.

### v0.9

Assistente de troubleshooting com IA para triagem de falhas de mensagens HL7/FHIR.

### v1.0

Healthcare Integration Platform pronta para validação através de piloto controlado.

---

## 8. Estratégia de evolução

O projeto seguirá a seguinte progressão:

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

Cada etapa deverá ser validada antes da próxima evolução.

---

## 9. Estratégias futuras de implantação

A arquitetura deverá permitir implantação em diferentes modelos.

### On-premise

Execução dentro da infraestrutura do cliente.

### Cloud

Execução em provedores como AWS, Azure ou Google Cloud.

### Hybrid

Componentes de integração local combinados com serviços em nuvem.

---

## 10. Stack inicial prevista

### Aplicação

- Python

### Interoperabilidade

- HL7v2
- MLLP
- FHIR R4
- REST APIs

### FHIR Server

- HAPI FHIR

### Persistência

- PostgreSQL

### Infraestrutura

- Docker
- Docker Compose

### Evoluções possíveis

- Redis
- RabbitMQ ou Kafka
- Prometheus
- Grafana
- OpenTelemetry

A inclusão de novas tecnologias deverá ocorrer apenas quando houver justificativa arquitetural ou operacional.

---

## 11. Método de desenvolvimento e documentação

Cada etapa técnica do projeto deverá conter:

1. Contexto teórico.
2. Problema que o componente resolve.
3. Papel do componente na arquitetura.
4. Decisão técnica adotada.
5. Implementação.
6. Configuração.
7. Testes.
8. Validação.
9. Troubleshooting.
10. Evidências.
11. Conclusão e próximos passos.

O objetivo é manter o projeto compreensível tanto do ponto de vista educacional quanto de engenharia.

---

## 12. Dados utilizados no projeto

Todos os exemplos e testes públicos do repositório deverão utilizar dados fictícios ou sintéticos.

Nenhuma informação real de paciente deverá ser armazenada no repositório.

---

## 13. Resultado esperado

Ao final da evolução do projeto, o repositório deverá demonstrar não apenas conhecimento dos padrões HL7v2 e FHIR, mas a capacidade de transformar esses padrões em uma solução de integração operacional, configurável, observável e potencialmente aplicável em ambientes reais de saúde.
