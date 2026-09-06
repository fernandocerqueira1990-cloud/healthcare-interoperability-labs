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
5. resultado no BigQuery.

Assim, a narrativa fica clara: **mensagem recebida → processada → estruturada → analisável**.

## Legendas curtas para as imagens

- **IAM:** “Permissões do service agent da Cloud Healthcare API para integração com Pub/Sub, Storage e BigQuery.”
- **MSA|AA:** “Confirmação de aceite da mensagem HL7v2 enviada via MLLP.”
- **Logs:** “Adaptador MLLP recebendo e enviando a mensagem ao HL7v2 Store.”
- **FHIR:** “Recurso Patient gerado a partir do fluxo de integração.”
- **BigQuery:** “Dados clínicos estruturados disponíveis para consulta analítica.”
