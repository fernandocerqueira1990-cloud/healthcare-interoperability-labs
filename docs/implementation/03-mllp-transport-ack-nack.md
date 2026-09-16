# Milestone 1.3 — Transporte MLLP + ACK/NACK

## 1. Objetivo

Implementar transporte real de mensagens HL7v2 entre o HIS Simulator e o Healthcare Integration Gateway utilizando TCP e MLLP, com geração de respostas HL7 ACK e correlação pelo `Message Control ID` (`MSH-10`).

Até o Milestone 1.2, as mensagens eram lidas e validadas diretamente a partir de arquivos locais. Neste milestone, a mensagem passa a trafegar por uma conexão de rede, aproximando o laboratório de um cenário real de integração hospitalar.

---

## 2. Arquitetura implementada

```text
HIS Simulator
     |
     | TCP / MLLP
     | HL7v2
     v
MLLP Receiver
     |
     +--> framing MLLP
     +--> leitura do MSH
     +--> MSH-9 / MSH-10
     +--> decisão AA / AE / AR
     |
     v
HL7 ACK
     |
     | TCP / MLLP
     v
HIS Simulator
```

---

## 3. MLLP

MLLP significa **Minimal Lower Layer Protocol**. É um mecanismo tradicional de transporte para mensagens HL7v2 sobre TCP.

HL7v2 define a estrutura e a semântica da mensagem; MLLP define como a mensagem é delimitada no fluxo TCP.

Framing utilizado:

```text
<VT> HL7 MESSAGE <FS><CR>
```

Em bytes:

```text
START_BLOCK     = 0x0B
END_BLOCK       = 0x1C
CARRIAGE_RETURN = 0x0D
```

Payload:

```text
0x0B + HL7 MESSAGE + 0x1C + 0x0D
```

---

## 4. Componentes criados

### 4.1 MLLP Receiver

Arquivo:

```text
src/gateway/receivers/mllp_receiver.py
```

Responsabilidades implementadas:

- abrir socket TCP;
- escutar na porta configurada;
- aceitar conexões;
- receber bytes;
- localizar o framing MLLP;
- extrair a mensagem HL7v2;
- identificar o segmento `MSH`;
- ler `MSH-9` e `MSH-10`;
- gerar ACK;
- retornar ACK por MLLP;
- registrar logs de conexão, mensagem e resposta.

Configuração padrão:

```text
HOST = 127.0.0.1
PORT = 2575
```

Também são aceitas as variáveis de ambiente:

```text
MLLP_HOST
MLLP_PORT
```

### 4.2 HIS Simulator MLLP Client

Arquivo:

```text
src/his-simulator/tools/send_mllp.py
```

Responsabilidades:

- carregar uma mensagem HL7v2 de arquivo;
- criar conexão TCP;
- aplicar framing MLLP;
- transmitir a mensagem;
- aguardar ACK;
- remover framing da resposta;
- exibir o ACK recebido;
- reconhecer `AA`, `AE` e `AR`.

Uso padrão:

```bash
python3 src/his-simulator/tools/send_mllp.py
```

Arquivo padrão:

```text
src/his-simulator/messages/adt_a01.hl7
```

Também é possível informar um arquivo diferente:

```bash
python3 src/his-simulator/tools/send_mllp.py \
src/his-simulator/messages/arquivo.hl7
```

---

## 5. ACK HL7v2

Neste milestone foram implementados três resultados de acknowledgement no segmento `MSA`.

### AA — Application Accept

Mensagem aceita.

```text
MSA|AA|MSG00001|Message accepted
```

### AE — Application Error

A mensagem foi recebida, mas apresentou erro de conteúdo/validação no processamento atual.

```text
MSA|AE||Missing Message Control ID
```

### AR — Application Reject

A mensagem foi rejeitada pelo gateway.

```text
MSA|AR|MSG00002|Unsupported message type
```

---

## 6. Correlação por Message Control ID

O `MSH-10` identifica a mensagem de origem.

Mensagem válida:

```text
MSH-10 = MSG00001
```

ACK:

```text
MSA|AA|MSG00001|Message accepted
```

Fluxo de correlação:

```text
ADT^A01
MSH-10 = MSG00001
        |
        v
Gateway
        |
        v
ACK
MSA-2 = MSG00001
```

---

## 7. Cenários validados

### Cenário 1 — Happy path

Entrada:

```text
MSH-9  = ADT^A01
MSH-10 = MSG00001
```

Resultado:

```text
AA
MSA|AA|MSG00001|Message accepted
ACK VALIDATION RESULT: PASS
```

### Cenário 2 — MSH-10 ausente

Entrada:

```text
MSH-9  = ADT^A01
MSH-10 = vazio
```

Resultado:

```text
AE
MSA|AE||Missing Message Control ID
ACK VALIDATION RESULT: PASS
```

### Cenário 3 — Tipo de mensagem não suportado

Entrada:

```text
MSH-9  = ORM^O01
MSH-10 = MSG00002
```

Como o MVP v0.1 aceita atualmente `ADT^A01`, o resultado foi:

```text
AR
MSA|AR|MSG00002|Unsupported message type
ACK VALIDATION RESULT: PASS
```

---

## 8. Troubleshooting — deslocamento de campos MSH

Durante o teste de `AE`, uma versão da mensagem inválida recebeu um separador `|` adicional no `MSH`:

```text
...|20260914231500|||ADT^A01||P|2.5
```

O efeito foi o deslocamento dos campos seguintes. O Receiver interpretou:

```text
MSH-9  = vazio
MSH-10 = ADT^A01
```

em vez de:

```text
MSH-9  = ADT^A01
MSH-10 = vazio
```

A investigação foi feita enumerando os campos resultantes do split:

```python
for i, value in enumerate(line.split("|")):
    print(f"index={i:02d} value={value!r}")
```

Estrutura correta observada:

```text
index 06 = timestamp
index 07 = vazio
index 08 = ADT^A01
index 09 = vazio
index 10 = P
index 11 = 2.5
```

Esse troubleshooting reforça uma característica central do HL7v2: campos posicionais dependem diretamente da quantidade correta de delimitadores.

---

## 9. Logs validados

Happy path:

```text
HL7 received | type=ADT^A01 | control_id=MSG00001
ACK generated | code=AA | correlation_id=MSG00001
```

Application Error:

```text
HL7 received | type=ADT^A01 | control_id=<missing>
HL7 validation failed | reason=missing MSH-10
ACK generated | code=AE | correlation_id=<missing>
```

Application Reject:

```text
HL7 received | type=ORM^O01 | control_id=MSG00002
HL7 rejected | reason=unsupported message type | type=ORM^O01
ACK generated | code=AR | correlation_id=MSG00002
```

---

## 10. Resultado

O Milestone 1.3 demonstrou com sucesso:

- comunicação TCP;
- framing MLLP;
- transmissão e recepção HL7v2;
- parsing básico do `MSH` para transporte;
- correlação por `MSH-10`;
- geração de ACK;
- `AA`, `AE` e `AR`;
- logs operacionais;
- testes positivos e negativos;
- troubleshooting de mensagem HL7v2 malformada.

O Healthcare Integration Gateway agora possui uma interface de entrada MLLP funcional.

---

## 11. Próximo milestone

**Milestone 1.4 — HL7 Parser + Validator Core desacoplados**

Objetivo arquitetural:

```text
MLLP Receiver
      |
      v
HL7 Parser
      |
      v
Validator Core
      |
      v
ACK Decision
```

O próximo passo é retirar progressivamente responsabilidades de parsing e validação do Receiver, preservando baixo acoplamento e testabilidade.
