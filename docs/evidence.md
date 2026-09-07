# Mapa de evidências

Este guia relaciona as evidências capturadas durante os laboratórios aos resultados técnicos que elas comprovam.

> Antes de publicar imagens, revise-as para não expor tokens, IDs temporários, endereços internos, dados reais de pacientes ou qualquer credencial.

## Evidências do Lab 01 — Ingesting HL7v2 Data

| Evidência | O que comprova | Valor para o portfólio |
|---|---|---|
| Tela de IAM com o Cloud Healthcare Service Agent e as funções atribuídas | Configuração de acesso entre serviços | Demonstra entendimento de IAM e integração gerenciada |
| Terminal com instalação do Netcat e execução do comando de envio | Preparação do teste de conectividade MLLP | Mostra execução prática e troubleshooting |
| Resposta `MSA|AA|` | Aceite da mensagem pelo fluxo HL7v2/MLLP | É a principal evidência de sucesso de transporte |
| Logs do MLLP Adapter com “Message was successfully sent” | Encaminhamento para a Healthcare API | Mostra a ponte entre protocolo legado e cloud |
| Resposta JSON contendo `hl7V2Messages` | Persistência no HL7v2 Store | Confirma o resultado final do laboratório |

### Organização sugerida

```text
assets/
└── evidence/
    ├── hl7v2-01-iam-service-agent.png
    ├── hl7v2-02-mllp-ack-aa.png
    ├── hl7v2-03-adapter-success-logs.png
    └── hl7v2-04-store-message-list.png
```

## Evidências do Lab 02 — Streaming HL7v2 para FHIR

| Evidência | O que comprova | Valor para o portfólio |
|---|---|---|
| Job Dataflow em estado `Running` | Pipeline contínuo de processamento | Demonstra arquitetura de dados em streaming |
| Pods `mllp-adapter` e `simhospital` em `Running` | Camada de integração executada em GKE | Mostra containers e Kubernetes aplicados a Healthcare IT |
| FHIR Viewer com recursos `Patient` | Conversão de dados para padrão FHIR | Demonstra interoperabilidade clínica moderna |
| Resultado de consulta no BigQuery | Persistência e consumo analítico | Conecta integração clínica a BI e dados |
| Saída `curl` do endpoint FHIR | Consulta via API REST autenticada | Demonstra uso prático da Healthcare API |

### Organização sugerida

```text
assets/
└── evidence/
    ├── streaming-01-gke-pods-running.png
    ├── streaming-02-dataflow-running.png
    ├── streaming-03-fhir-patient-resource.png
    ├── streaming-04-bigquery-patient-query.png
    └── streaming-05-fhir-rest-api-response.png
```

## Ordem recomendada para apresentação

Para uma leitura rápida no GitHub ou LinkedIn, use esta sequência:

1. Arquitetura;
2. execução do MLLP Adapter e a confirmação `MSA|AA|`;
3. pipeline/Dataflow ou pods em execução;
4. recurso `Patient` no FHIR Viewer;
5. fluxo DICOM Store → BigQuery;
6. recurso FHIR original e sua versão desidentificada;
7. resultado no BigQuery.

Assim, a narrativa fica clara: **mensagem recebida → processada → estruturada → analisável**.

## Legendas curtas para as imagens

- **IAM:** “Permissões do service agent da Cloud Healthcare API para integração com Pub/Sub, Storage e BigQuery.”
- **MSA|AA:** “Confirmação de aceite da mensagem HL7v2 enviada via MLLP.”
- **Logs:** “Adaptador MLLP recebendo e enviando a mensagem ao HL7v2 Store.”
- **FHIR:** “Recurso Patient gerado a partir do fluxo de integração.”
- **BigQuery:** “Dados clínicos estruturados disponíveis para consulta analítica.”
- **DICOM Store:** “Imagens médicas ingeridas no Cloud Healthcare API e preparadas para consulta por DICOMweb.”
- **DICOM → BigQuery:** “Metadados de estudos de imagem disponibilizados para análise sem acessar os arquivos DICOM diretamente.”
- **Troubleshooting DICOM:** “Retorno da API analisado para corrigir permissões do service agent e a dependência do dataset analítico.”

## Evidências do Lab 04 — Ingesting FHIR Data

| Evidência | O que comprova | Valor para o portfólio |
|---|---|---|
| Datasets BigQuery criados | Separação de camadas analíticas original e desidentificada | Demonstra preparação de dados para governança e analytics |
| FHIR Stores R4 e tópico Pub/Sub | Recursos de interoperabilidade e notificação configurados | Mostra arquitetura orientada a eventos |
| Importação FHIR | Recursos carregados do Cloud Storage | Demonstra carga em massa de dados padronizados |
| Consultas original e desidentificada | Transformação de atributos pessoais validada em SQL | Demonstra privacidade e governança aplicadas a dados clínicos |
| `PATCH` de `streamConfigs` | Configuração de exportação contínua para BigQuery | Mostra administração da API e integração em tempo próximo do real |
| `POST` de Patient e consulta posterior | Recurso criado por API e refletido na camada analítica | Valida o fluxo ponta a ponta FHIR → BigQuery |

### Organização adotada

```text
assets/
└── evidence/
    ├── fhir-01-project-and-bigquery-datasets.png
    ├── fhir-02-stores-r4-and-pubsub.png
    ├── fhir-03-import-resources-success.png
    ├── fhir-04-original-patient-query.png
    ├── fhir-05-deidentified-patient-query.png
    ├── fhir-06-streaming-configuration.png
    ├── fhir-07-patient-rest-create.png
    └── fhir-08-streaming-patient-query.png
```

## Evidências do Lab 03 — Ingesting DICOM Data

| Evidência | O que comprova | Valor para o portfólio |
|---|---|---|
| IAM do Cloud Healthcare Service Agent | Permissões para Healthcare API, Storage e BigQuery | Demonstra governança de acesso entre serviços gerenciados |
| Criação dos DICOM Stores e importação | Provisionamento por CLI/REST e ingestão de arquivos `.dcm` | Mostra operação prática de PACS/RIS em cloud |
| Retorno `400` e correção | Diagnóstico de IAM e dataset ausente | Evidencia troubleshooting orientado ao retorno da API |
| Dataset BigQuery e operação de exportação | Camada analítica criada e exportação assíncrona iniciada | Conecta imagem médica a dados estruturados |
| Consulta por `PatientID` | Metadados DICOM consultáveis em SQL | Valida o fluxo ponta a ponta |
| Consulta `No Finding` | Segmentação analítica e interpretação semântica | Demonstra cuidado com significado clínico dos campos |

### Organização adotada

```text
assets/
└── evidence/
    ├── dicom-01-iam-service-agent.png
    ├── dicom-02-store-provisioning-and-import.png
    ├── dicom-03-export-permission-troubleshooting.png
    ├── dicom-04-bigquery-dataset-and-export-success.png
    ├── dicom-05-bigquery-study-query.png
    └── dicom-06-bigquery-no-finding-query.png
```
