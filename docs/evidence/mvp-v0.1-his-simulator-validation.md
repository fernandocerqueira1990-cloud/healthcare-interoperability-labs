# Evidência — MVP v0.1 / Milestone 1.2

## Escopo

Validação estrutural de mensagem HL7v2 `ADT^A01` sintética no HIS Simulator.

## Evidências executadas

### 1. Inspeção de campos

O utilitário `inspect_hl7.py` confirmou os principais campos preenchidos dos segmentos `MSH`, `EVN`, `PID` e `PV1`.

Pontos críticos validados:

```text
MSH-9: ADT^A01
MSH-10: MSG00001
MSH-12: 2.5
PID-3: <identificador sintético>
PID-5: <nome sintético>
PV1-2: I
PV1-19: VN00001
PV1-44: 20260914231500
```

### 2. Happy path

Execução do validador com mensagem completa:

```bash
python3 src/his-simulator/tools/validate_adt_a01.py
```

Resultado observado:

```text
VALIDATION RESULT: PASS
```

### 3. Teste negativo

O campo `PV1-19 (Visit Number)` foi removido intencionalmente.

Resultado observado:

```text
[ERROR] PV1-19 (Visit Number) vazio ou ausente
VALIDATION RESULT: FAIL
```

### 4. Recuperação

O arquivo original foi restaurado e o validador executado novamente.

Resultado observado:

```text
[OK] PV1-19 (Visit Number) = VN00001
VALIDATION RESULT: PASS
```

## Troubleshooting registrado

Também foi identificado e corrigido um erro inicial de posicionamento do `Visit Number`, causado por quantidade incorreta de delimitadores no `PV1`.

Após a correção, a ferramenta de inspeção confirmou:

```text
PV1-19: VN00001
PV1-44: 20260914231500
```

## Conclusão

O laboratório demonstrou três capacidades essenciais:

1. inspeção estrutural de mensagens HL7v2;
2. validação automática de campos mínimos do fluxo ADT^A01;
3. detecção e recuperação de uma inconsistência controlada.

Padrão operacional adotado:

```text
detectar -> isolar -> validar -> corrigir -> revalidar -> documentar
```
