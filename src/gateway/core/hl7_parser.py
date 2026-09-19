import re
from dataclasses import dataclass
from typing import Dict


@dataclass
class ParsedHL7Message:
    raw_message: str
    segments: Dict[str, Dict[int, str]]
    message_type: str
    trigger_event: str
    message_control_id: str
    processing_id: str
    version_id: str


def split_segments(message: str):
    """
    Normaliza diferentes tipos de quebra de linha encontrados
    em mensagens HL7v2 e retorna apenas segmentos não vazios.
    """
    return [
        segment.strip()
        for segment in re.split(r"\r\n|\r|\n", message)
        if segment.strip()
    ]
def parse_segment(
    segment: str,
    field_separator: str = "|",
):
    """
    Converte um segmento HL7 em um dicionário de campos.

    O segmento MSH exige tratamento especial porque:
    - MSH-1 é o field separator;
    - MSH-2 contém os encoding characters.

    Para os demais segmentos, utiliza o separador
    definido pelo MSH-1 da mensagem.
    """
    if len(segment) < 3:
        raise ValueError("Invalid HL7 segment")

    segment_name = segment[:3]

    if segment_name == "MSH":
        if len(segment) < 4:
            raise ValueError("Invalid MSH segment")

        field_separator = segment[3]
        raw_fields = segment.split(field_separator)

        fields = {
            1: field_separator,
        }

        for index, value in enumerate(
            raw_fields[1:],
            start=2,
        ):
            fields[index] = value

        return segment_name, fields

    raw_fields = segment.split(field_separator)

    fields = {
        index: value
        for index, value in enumerate(
            raw_fields[1:],
            start=1,
        )
    }

    return segment_name, fields

def parse_message(message: str) -> ParsedHL7Message:
    """
    Faz parsing estrutural básico de uma mensagem HL7v2.

    Esta função não executa regras de negócio nem decide
    se a mensagem deve ser aceita ou rejeitada.

    Responsabilidade:
        raw HL7 -> representação interna previsível
    """
    if not message or not message.strip():
        raise ValueError("HL7 message is empty")

    raw_segments = split_segments(message)

    msh_segment = next(
        (
            segment
            for segment in raw_segments
            if segment.startswith("MSH")
        ),
        None,
    )

    if msh_segment is None:
        raise ValueError("MSH segment not found")

    if len(msh_segment) < 4:
        raise ValueError("Invalid MSH segment")

    field_separator = msh_segment[3]

    segments = {}

    for segment in raw_segments:
        segment_name, fields = parse_segment(
            segment,
            field_separator=field_separator,
        )

        segments[segment_name] = fields

    msh = segments["MSH"]

    message_type = msh.get(9, "")
    message_control_id = msh.get(10, "")
    processing_id = msh.get(11, "")
    version_id = msh.get(12, "")

    trigger_event = ""

    if "^" in message_type:
        parts = message_type.split("^")

        if len(parts) > 1:
            trigger_event = parts[1]

    return ParsedHL7Message(
        raw_message=message,
        segments=segments,
        message_type=message_type,
        trigger_event=trigger_event,
        message_control_id=message_control_id,
        processing_id=processing_id,
        version_id=version_id,
    )
