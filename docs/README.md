# Índice da Documentação

Este diretório organiza a documentação técnica do projeto **Healthcare Interoperability Labs / Healthcare Integration Gateway**.

A documentação é dividida entre a base de estudos já concluída em Google Cloud e a evolução prática para um gateway de interoperabilidade local, modular e reproduzível.

---

## 1. Produto

- [Product Vision](product-vision.md) — problema, objetivo, princípios arquiteturais, MVP e evolução LAB → PoC → MVP → Piloto → Produto.
- [Status do projeto](project-status.md) — visão consolidada do que já foi concluído e do próximo passo.

---

## 2. Arquitetura do Healthcare Integration Gateway

- [Arquitetura v0.1](architecture/01-overview.md) — visão lógica, responsabilidades dos componentes, baixo acoplamento, observabilidade e desenho do MVP.
- [Fluxo ADT^A01 → FHIR](architecture/02-adt-a01-flow.md) — fluxo funcional de admissão hospitalar, origem HL7v2 e destino FHIR.
- [Fluxo MLLP + ACK](architecture/03-mllp-ack-flow.md) — transporte TCP/MLLP, framing, correlação por `MSH-10` e decisão `AA` / `AE` / `AR`.

---

## 3. Implementação

- [01 — Ambiente FHIR Local](implementation/01-local-fhir-environment.md)
  - HAPI FHIR R4;
  - PostgreSQL;
  - Docker Compose;
  - rede interna;
  - volume persistente;
  - CapabilityStatement;
  - criação e busca de Patient;
  - teste de persistência.

- [02 — HIS Simulator + HL7v2 ADT^A01](implementation/02-his-simulator-adt-a01.md)
  - estrutura ADT^A01;
  - MSH, EVN, PID e PV1;
  - inspeção de campos HL7;
  - particularidade do parsing de MSH;
  - validação estrutural;
  - teste negativo controlado;
  - troubleshooting de posição de campos;
  - relação conceitual com FHIR e InterSystems.

- [03 — Transporte MLLP + ACK/NACK](implementation/03-mllp-transport-ack-nack.md)
  - socket TCP;
  - framing MLLP;
  - Receiver na porta 2575;
  - HIS Simulator MLLP Client;
  - leitura de `MSH-9` e `MSH-10`;
  - ACK com `AA`, `AE` e `AR`;
  - correlação por Message Control ID;
  - logs operacionais;
  - troubleshooting de deslocamento de campos no `MSH`.

- [04 — HL7 Parser + Validator Core](implementation/04-hl7-parser-validator-core.md)
  - `ParsedHL7Message`;
  - separação transporte / parsing / validação;
  - `MSH-1` como field separator;
  - `ValidationResult`;
  - AA / AE / AR preservados;
  - 6 testes automatizados;
  - troubleshooting de execução como módulo;
  - limitação conhecida de segmentos repetidos.

- [05 — ADT^A01 → FHIR Patient + Encounter](implementation/05-adt-a01-fhir-patient-encounter.md)
  - mapping `PID → Patient`;
  - mapping `PV1 → Encounter`;
  - FHIR Client;
  - ADT A01 Service;
  - vínculo real `Encounter.subject.reference`;
  - integração com MLLP Receiver;
  - 8 testes automatizados consolidados;
  - persistência end-to-end no HAPI FHIR.

---

## 4. Evidências

- [MVP v0.1 — Validação do Ambiente FHIR Local](evidence/mvp-v0.1-local-fhir-validation.md)
- [MVP v0.1 — Validação do HIS Simulator / ADT^A01](evidence/mvp-v0.1-his-simulator-validation.md)
- [MVP v0.1 — Validação MLLP + ACK/NACK](evidence/mvp-v0.1-mllp-ack-validation.md)
- [MVP v0.1 — Validação HL7 Parser + Validator Core](evidence/mvp-v0.1-hl7-parser-validator-validation.md)\n- [MVP v0.1 — Validação end-to-end ADT^A01 → FHIR](evidence/mvp-v0.1-adt-a01-fhir-e2e-validation.md)

Os documentos registram comandos, resultados esperados, resultados observados, interpretação técnica, testes positivos e negativos e troubleshooting.

---

## 5. Relatórios técnicos

- [Milestone 1.1 — Ambiente FHIR Local](reports/01-milestone-1.1-summary.md)
- [Milestone 1.2 — HIS Simulator + HL7v2 ADT^A01](reports/02-milestone-1.2-summary.md)
- [Milestone 1.3 — Transporte MLLP + ACK/NACK](reports/03-milestone-1.3-summary.md)
- [Milestone 1.4 — HL7 Parser + Validator Core](reports/04-milestone-1.4-summary.md)\n- [Milestone 1.5 — ADT^A01 → FHIR Patient + Encounter](reports/05-milestone-1.5-summary.md)

---

## 6. Guia de estudo / preparação técnica

- [InterSystems Technical Specialist — Guia de estudo](study/intersystems-technical-specialist-interview-guide.md)

O guia consolida siglas, arquitetura, HL7v2, FHIR, MLLP, ACK/NACK, HIS/RIS/LIS/PACS, troubleshooting, SQL, conceitos InterSystems e relação com os cases profissionais e o laboratório.

---

## 7. Laboratórios Google Cloud já concluídos

Esses laboratórios formam a base conceitual que está sendo levada para a implementação própria do gateway.

- [01 — Ingesting HL7v2 Data with the Healthcare API](01-ingesting-hl7v2.md)
- [02 — Streaming HL7v2 to FHIR](02-streaming-hl7v2-to-fhir.md)
- [03 — Ingesting DICOM](03-ingesting-dicom.md)
- [04 — Ingesting FHIR](04-ingesting-fhir.md)
- [Arquitetura consolidada dos labs](architecture.md)
- [Mapa de evidências](evidence.md)
- [Roadmap original](roadmap.md)

---

## 8. Regra de documentação do projeto

Cada nova fase deve registrar, sempre que aplicável:

1. contexto teórico;
2. problema que o componente resolve;
3. papel na arquitetura;
4. decisão técnica;
5. implementação;
6. configuração;
7. testes;
8. validação;
9. troubleshooting;
10. evidências;
11. conclusão;
12. próximos passos.

A intenção é que o repositório sirva simultaneamente como documentação de engenharia, material de estudo, portfólio técnico e base de evolução para um produto real.
