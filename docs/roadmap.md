# Roadmap de aprendizado

## Trilha concluída

```mermaid
flowchart LR
    A["HL7v2 + MLLP"] --> B["HL7v2 → FHIR"]
    B --> C["FHIR direto"]
    C --> D["DICOM"]
```

| Etapa | Status | Resultado |
|---|---|---|
| Ingesting HL7v2 Data with the Healthcare API | Concluída | Mensagem HL7v2 recebida por MLLP e persistida no HL7v2 Store |
| Streaming HL7 to FHIR Data with Healthcare API | Concluída | Dados HL7v2 convertidos em FHIR e disponibilizados no BigQuery |
| Ingesting FHIR Data with the Healthcare API | Próxima | Criar, importar, consultar e gerenciar recursos FHIR diretamente |
| Ingesting DICOM Data with the Healthcare API | Próxima | Ingerir e organizar imagens médicas no DICOM Store |

## Próximo laboratório: FHIR

A prioridade é praticar a ingestão direta de FHIR.

Isso complementa o lab de streaming ao mostrar o caminho em que uma aplicação já produz ou consome recursos FHIR via API REST, sem depender de uma mensagem HL7v2 na origem.

Pontos esperados de aprendizado:

- estrutura de recursos como `Patient`, `Observation`, `Encounter` e `MedicationRequest`;
- criação e consulta via API REST;
- organização de dados clínicos em FHIR Store;
- diferenças entre integração baseada em mensagens e integração baseada em recursos;
- noções de busca, versionamento e validação.

## Depois: DICOM

O estudo de DICOM completa a terceira modalidade principal da Healthcare API.

Pontos esperados de aprendizado:

- DICOM Store;
- estudos, séries e instâncias;
- integração com PACS/RIS;
- DICOMweb;
- gestão de imagens médicas na nuvem;
- possibilidades de desidentificação para pesquisa.

## Competência resultante

Ao concluir a trilha, o portfólio cobrirá as três modalidades principais de dados em saúde:

| Modalidade | Papel | Sistemas comuns |
|---|---|---|
| HL7v2 | Eventos e mensageria clínica | HIS, LIS, EHR, integração legada |
| FHIR | Recursos clínicos e APIs modernas | Aplicativos, portais, integrações digitais |
| DICOM | Imagens médicas | PACS, RIS, radiologia e diagnóstico por imagem |

## Próximos aprofundamentos recomendados

1. Perfis, extensões e terminologias FHIR;
2. LGPD, segurança, auditoria e desidentificação;
3. observabilidade de integrações clínicas;
4. qualidade de dados, reprocessamento e idempotência;
5. dashboards de integração e indicadores operacionais;
6. arquitetura híbrida entre datacenter hospitalar e cloud.
