# Guia de Estudo — InterSystems Technical Specialist

> Material de revisão técnica e de entrevista baseado no Healthcare Interoperability Labs, na vaga Technical Specialist e nos conceitos estudados durante o Milestone 1.2.

## 1. Visão geral da arquitetura de interoperabilidade

```text
Sistema origem / HIS
       |
       | evento clínico ou administrativo
       v
Mensagem HL7v2
       |
       | normalmente MLLP em integrações legadas
       v
Camada de integração
       |
       +--> recepção
       +--> parsing
       +--> validação
       +--> regras / routing
       +--> transformação
       +--> logs / rastreabilidade
       v
Sistema destino / API / FHIR / LIS / RIS / PACS
       |
       v
ACK / NACK / resposta
```

A camada de integração desacopla sistemas. O HIS não precisa conhecer todos os detalhes internos de cada destino; a engine recebe, interpreta, valida, transforma e encaminha mensagens.

## 2. HIS

**HIS — Hospital Information System**.

Sistema de informação hospitalar responsável por centralizar processos clínicos e administrativos como cadastro, atendimento, internação, prontuário, ordens, resultados, faturamento e outros fluxos.

Exemplos relacionados à experiência profissional: SMART Pixeon e TechSallus. TrakCare é o HIS/EHR da InterSystems relacionado à vaga.

## 3. EHR / EMR / PEP

- **EHR — Electronic Health Record**: registro eletrônico longitudinal de saúde, com visão mais ampla e interoperável.
- **EMR — Electronic Medical Record**: registro médico eletrônico normalmente mais ligado a uma instituição/serviço.
- **PEP — Prontuário Eletrônico do Paciente**: termo comum no Brasil para o prontuário digital.

Na prática comercial os termos podem se sobrepor, mas em interoperabilidade o ponto principal é entender que dados clínicos precisam circular entre sistemas mantendo identificação, contexto e significado.

## 4. HL7

**HL7 — Health Level Seven**.

Família de padrões de interoperabilidade em saúde. O “Level Seven” faz referência histórica à camada de aplicação do modelo OSI.

### HL7 v2

Muito usado para mensageria baseada em eventos entre sistemas hospitalares.

Exemplos:

- paciente admitido -> ADT;
- ordem de exame -> ORM;
- resultado -> ORU;
- agendamento -> SIU.

Estrutura em segmentos separados por delimitadores.

## 5. ADT

**ADT — Admission, Discharge and Transfer**.

Família de mensagens para movimentações administrativas do paciente.

Exemplos:

- `ADT^A01` — admissão;
- `ADT^A03` — alta;
- `ADT^A08` — atualização de dados.

No laboratório atual foi implementado `ADT^A01`.

## 6. A01

Evento de admissão / visit notification.

Fluxo típico:

```text
Paciente admitido
  -> HIS registra evento
  -> gera ADT^A01
  -> engine de integração recebe
  -> sistemas dependentes são atualizados
```

## 7. Segmentos HL7 usados no laboratório

### MSH — Message Header

Cabeçalho da mensagem.

Campos importantes:

- `MSH-1` — Field Separator;
- `MSH-2` — Encoding Characters;
- `MSH-3` — Sending Application;
- `MSH-4` — Sending Facility;
- `MSH-5` — Receiving Application;
- `MSH-6` — Receiving Facility;
- `MSH-7` — Date/Time of Message;
- `MSH-9` — Message Type;
- `MSH-10` — Message Control ID;
- `MSH-11` — Processing ID;
- `MSH-12` — Version ID.

### Particularidade de MSH

`MSH` é especial porque o caractere imediatamente após `MSH` é o próprio `MSH-1`. Por isso um parser ingênuo usando somente `split('|')` desloca a numeração dos campos.

### EVN — Event Type

Informações relacionadas ao evento ADT e seu timestamp.

### PID — Patient Identification

Identificação e dados demográficos do paciente.

Campos relevantes:

- `PID-3` — Patient Identifier List;
- `PID-5` — Patient Name;
- `PID-7` — Date of Birth;
- `PID-8` — Administrative Sex;
- `PID-11` — Patient Address;
- `PID-13` — Phone Number.

### PV1 — Patient Visit

Informações do atendimento/episódio.

Campos relevantes:

- `PV1-2` — Patient Class;
- `PV1-3` — Assigned Patient Location;
- `PV1-7` — Attending Doctor;
- `PV1-19` — Visit Number;
- `PV1-44` — Admit Date/Time.

## 8. Patient Identifier x Visit Number

São conceitos diferentes.

- Patient Identifier identifica a pessoa/paciente.
- Visit Number identifica um episódio específico.

```text
Paciente 123
  |-- Visita A
  |-- Visita B
  `-- Visita C
```

Essa distinção é essencial em troubleshooting de integrações.

## 9. Delimitadores HL7

Exemplo:

```text
MSH|^~\&|...
```

- `|` — Field Separator;
- `^` — Component Separator;
- `~` — Repetition Separator;
- `\` — Escape Character;
- `&` — Subcomponent Separator.

Campos vazios continuam ocupando posição. Um delimitador a mais ou a menos pode deslocar o significado de todos os campos seguintes.

## 10. Message Control ID

`MSH-10`.

Identificador utilizado para rastrear/correlacionar a mensagem. Importante para:

- logs;
- troubleshooting;
- ACK/NACK;
- auditoria;
- rastreabilidade.

## 11. MLLP

**MLLP — Minimal Lower Layer Protocol**.

Protocolo de transporte muito comum para mensagens HL7v2 sobre TCP.

Ele não define o significado clínico da mensagem; apenas delimita início e fim do payload para transporte.

Fluxo futuro do projeto:

```text
HIS Simulator
   |
   | MLLP/TCP
   v
MLLP Receiver
   |
   v
Parser / Validator
```

## 12. ACK / NACK

**ACK — Acknowledgment**.

Confirma o resultado do recebimento/processamento de uma mensagem.

Códigos clássicos:

- `AA` — Application Accept;
- `AE` — Application Error;
- `AR` — Application Reject.

“NACK” é usado de forma genérica para resposta negativa, embora HL7 v2 normalmente represente isso pelos códigos de acknowledgment apropriados.

## 13. Parsing x validação

### Parsing

Transformar uma mensagem textual em estrutura interpretável.

Pergunta respondida:

> O que existe nesta mensagem e em que campo está?

### Validação

Aplicar regras sobre a estrutura interpretada.

Pergunta respondida:

> Esta mensagem atende aos requisitos mínimos esperados para este fluxo?

No projeto:

- `inspect_hl7.py` inspeciona;
- `validate_adt_a01.py` aplica validações mínimas.

## 14. Troubleshooting feito no Milestone 1.2

Problema inicial:

- Visit Number caiu em `PV1-18` em vez de `PV1-19`.

Causa:

- número incorreto de delimitadores vazios.

Correção:

- ajustar a linha PV1;
- executar inspeção automatizada;
- confirmar `PV1-19` e `PV1-44`.

Teste negativo:

- remover propositalmente `PV1-19`;
- validador retornar `FAIL`;
- restaurar arquivo;
- validador retornar `PASS`.

Padrão mental:

```text
detectar -> isolar -> validar -> corrigir -> revalidar -> documentar
```

## 15. FHIR

**FHIR — Fast Healthcare Interoperability Resources**.

Padrão moderno da HL7 baseado em recursos e muito associado a APIs HTTP/REST.

Recursos importantes:

- `Patient` — paciente;
- `Encounter` — atendimento/episódio;
- `Observation` — observação/resultado clínico;
- `ServiceRequest` — solicitação de serviço/exame;
- `DiagnosticReport` — relatório diagnóstico.

No roadmap:

```text
HL7v2 PID -> FHIR Patient
HL7v2 PV1 -> FHIR Encounter
```

## 16. HL7v2 x FHIR

HL7v2:

- orientado a mensagens/eventos;
- muito usado em sistemas legados e integração hospitalar;
- frequentemente transportado por MLLP.

FHIR:

- orientado a recursos;
- APIs REST são comuns;
- melhor encaixe com aplicações modernas e integração baseada em web.

Eles não são concorrentes absolutos. Muitos ambientes transformam eventos HL7v2 em recursos FHIR.

## 17. REST API

**REST — Representational State Transfer**.

Padrão arquitetural frequentemente usado em APIs HTTP.

Métodos comuns:

- GET — consultar;
- POST — criar;
- PUT/PATCH — atualizar;
- DELETE — remover.

No Milestone 1.1, HAPI FHIR foi acessado via REST.

## 18. HAPI FHIR

Implementação open source de FHIR em Java.

No projeto funciona como servidor FHIR R4 local, expondo endpoints e persistindo recursos no PostgreSQL.

## 19. FHIR R4

Release 4 do padrão FHIR. O ambiente local usa FHIR 4.0.1 / R4.

## 20. PostgreSQL

Banco relacional utilizado como persistência do HAPI FHIR no laboratório.

## 21. PACS

**PACS — Picture Archiving and Communication System**.

Sistema de armazenamento, gerenciamento e distribuição de imagens médicas.

Experiência relevante: integração HIS/TechSallus com PACS Aurora Pixeon.

## 22. RIS

**RIS — Radiology Information System**.

Gerencia processos de radiologia: agenda, workflow, exames, laudos e integração com PACS/HIS.

## 23. LIS

**LIS — Laboratory Information System**.

Sistema de informação laboratorial. Recebe ordens, acompanha processamento e devolve resultados ao HIS/EMR.

Exemplo de fluxo:

```text
HIS --ORM--> LIS
HIS <--ORU-- LIS
```

## 24. DICOM

**DICOM — Digital Imaging and Communications in Medicine**.

Padrão para imagens médicas e comunicação associada. É diferente de HL7/FHIR: DICOM é fortemente orientado a imagens e workflow de imagem.

## 25. TrakCare

HIS/EHR integrado da InterSystems para processos clínicos e administrativos.

Na entrevista, não afirmar experiência em produção com TrakCare. A mensagem correta é:

> Tenho experiência com outros HIS e com processos hospitalares; minha curva de aprendizagem está no stack específico InterSystems, não em aprender Healthcare IT do zero.

## 26. InterSystems IRIS for Health

Plataforma de dados e interoperabilidade especializada em Healthcare no ecossistema InterSystems.

Para entrevista, entender seu papel como base tecnológica para dados, integração e aplicações de saúde.

## 27. Production — InterSystems

Uma Production organiza componentes de interoperabilidade que recebem, processam e enviam mensagens.

Modelo mental:

```text
Business Service
      |
      v
Business Process
      |
      v
Business Operation
```

## 28. Business Service

Componente de entrada.

Responsabilidade conceitual:

- receber mensagem/evento de sistema externo;
- iniciar o fluxo dentro da Production.

No laboratório, o futuro MLLP Receiver cumpre papel conceitualmente parecido.

## 29. Business Process

Componente para lógica de processamento/orquestração.

Pode envolver:

- decisões;
- regras;
- roteamento;
- transformação;
- coordenação de etapas.

## 30. Business Operation

Componente de saída responsável por comunicação com o destino.

Exemplo conceitual:

- enviar mensagem ao LIS;
- chamar endpoint externo;
- transmitir integração ao sistema destino.

## 31. Routing Rule

Regra de roteamento. Decide para onde a mensagem deve seguir de acordo com conteúdo ou contexto.

Exemplo:

```text
Se tipo = ADT^A01 -> destino A
Se tipo = ORU -> destino B
```

## 32. DTL

**Data Transformation Language** no contexto InterSystems.

Usada para transformação/mapeamento entre estruturas de dados/mensagens.

Modelo mental:

```text
mensagem origem
   -> mapeamento / transformação
   -> mensagem destino
```

## 33. Message Viewer

Ferramenta para visualizar mensagens processadas e investigar fluxo/conteúdo durante troubleshooting.

## 34. Visual Trace

Ferramenta para acompanhar visualmente o caminho de uma mensagem pelos componentes da Production.

Em entrevista, relacionar com seu método habitual de rastrear onde o fluxo parou.

## 35. SQL

**SQL — Structured Query Language**.

Experiência real relevante:

- SQL Server;
- MySQL;
- PostgreSQL;
- consultas;
- JOINs;
- views;
- procedures;
- índices;
- execution plans;
- investigação de inconsistências;
- performance.

## 36. RCA

**RCA — Root Cause Analysis**.

Análise de causa raiz. Objetivo não é somente restaurar o serviço, mas identificar por que ocorreu e como evitar repetição.

## 37. MTTR

**MTTR — Mean Time To Repair/Restore/Resolve**, conforme contexto operacional.

Métrica relacionada ao tempo médio para recuperação/resolução. Experiência profissional informa redução aproximada de 35% por meio de RCA, priorização e procedimentos.

## 38. SLA

**SLA — Service Level Agreement**.

Acordo de nível de serviço. Define expectativas como disponibilidade, tempo de resposta e resolução.

## 39. N2 / N3

Níveis de suporte técnico.

- N2: análise técnica especializada além do atendimento inicial;
- N3: análise avançada, problemas complexos, integração com desenvolvimento/engenharia e causa raiz.

## 40. Go-live

Entrada de uma solução em produção.

Ciclo mental:

```text
requisitos -> configuração -> testes -> homologação -> treinamento -> go-live -> estabilização
```

Durante go-live é importante:

- validar acessos;
- validar integrações;
- monitorar processos críticos;
- priorizar incidentes;
- manter comunicação com cliente;
- documentar ajustes.

## 41. Homologação

Etapa de validação funcional/técnica antes da produção. Confirma que processos, dados e integrações atendem ao esperado.

## 42. Estratégia de troubleshooting para entrevista

Caso: resultado de laboratório não chega ao HIS.

Raciocínio:

1. confirmar impacto e escopo;
2. verificar se o sistema origem gerou a mensagem;
3. confirmar se a integração recebeu;
4. validar estrutura HL7;
5. verificar routing;
6. verificar transformação;
7. verificar filas/logs;
8. verificar sistema destino;
9. analisar ACK/NACK;
10. corrigir de forma controlada;
11. validar end-to-end;
12. documentar RCA e prevenção.

## 43. Resposta para falta de experiência com TrakCare

> Todavía no he trabajado directamente con TrakCare en producción. Lo que sí tengo es experiencia con otros HIS hospitalarios, implementación, SQL, integraciones, soporte crítico y ambientes productivos. Mi curva de aprendizaje estaría principalmente en la tecnología específica de InterSystems, no en empezar desde cero en Healthcare IT.

## 44. Principal case profissional

TechSallus / MedSênior:

- levantamento de requisitos;
- parametrização;
- testes;
- homologação;
- capacitação;
- go-live;
- estabilização;
- integração HIS/PACS Aurora Pixeon.

Mensagem-chave: experiência técnica + funcional + cliente + operação.

## 45. Case de incidentes críticos

NovaVision/IPTEL:

- N2/N3;
- serviços críticos;
- análise por camadas;
- logs;
- banco;
- aplicação;
- infraestrutura;
- RCA;
- documentação;
- redução de MTTR.

## 46. Projeto pessoal para citar

Healthcare Interoperability Labs.

Resumo em espanhol:

> Estoy desarrollando un laboratorio personal de interoperabilidad clínica. Ya tengo un servidor FHIR R4 con HAPI FHIR y PostgreSQL en Docker y estoy construyendo el flujo desde un HIS simulado con HL7v2 ADT^A01, validación estructural y, en la próxima etapa, MLLP y ACK/NACK. El objetivo no es solamente hacer funcionar el código, sino documentar arquitectura, pruebas, troubleshooting y evidencias.

## 47. Mapa final — projeto x InterSystems

| Projeto | Conceito InterSystems |
|---|---|
| HIS Simulator | sistema origem / sistema externo |
| mensagem ADT^A01 | HL7 Message |
| MLLP Receiver | Business Service |
| Parser / processamento | Business Process (conceitual) |
| Validator | lógica de validação no processamento |
| Router | Routing Rule / Business Process |
| Transformer | DTL |
| Sender | Business Operation |
| pipeline | Production |
| logs / tracing | Message Viewer / Visual Trace |
| HAPI FHIR | destino/API FHIR externo |

> A associação é conceitual; o projeto não implementa o stack InterSystems.

## 48. Regra para a entrevista

Não tentar provar domínio de uma tecnologia que ainda não foi usada profissionalmente.

Priorizar:

- Healthcare IT real;
- implantação;
- integração;
- SQL;
- troubleshooting;
- cliente;
- go-live;
- capacidade de aprender rapidamente;
- raciocínio estruturado.
