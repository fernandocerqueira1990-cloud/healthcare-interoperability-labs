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

---

## 4. Evidências

- [MVP v0.1 — Validação do Ambiente FHIR Local](evidence/mvp-v0.1-local-fhir-validation.md)

O documento registra comandos, resultados esperados, resultados observados e interpretação técnica dos testes.

---

## 5. Laboratórios Google Cloud já concluídos

Esses laboratórios formam a base conceitual que está sendo levada para a implementação própria do gateway.

- [01 — Ingesting HL7v2 Data with the Healthcare API](01-ingesting-hl7v2.md)
- [02 — Streaming HL7v2 to FHIR](02-streaming-hl7v2-to-fhir.md)
- [03 — Ingesting DICOM](03-ingesting-dicom.md)
- [04 — Ingesting FHIR](04-ingesting-fhir.md)
- [Arquitetura consolidada dos labs](architecture.md)
- [Mapa de evidências](evidence.md)
- [Roadmap original](roadmap.md)

---

## 6. Regra de documentação do projeto

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
