from dataclasses import dataclass, field
from typing import List

from src.gateway.core.hl7_parser import ParsedHL7Message


@dataclass
class ValidationResult:
    valid: bool
    ack_code: str
    reason: str
    errors: List[str] = field(default_factory=list)


SUPPORTED_MESSAGE_TYPES = {
    "ADT^A01",
}


def validate_required_segment(
    message: ParsedHL7Message,
    segment_name: str,
    errors: List[str],
):
    if segment_name not in message.segments:
        errors.append(
            f"Missing required segment: {segment_name}"
        )


def validate_required_field(
    message: ParsedHL7Message,
    segment_name: str,
    field_number: int,
    description: str,
    errors: List[str],
):
    value = (
        message.segments
        .get(segment_name, {})
        .get(field_number, "")
    )

    if not value:
        errors.append(
            f"Missing required field: "
            f"{segment_name}-{field_number} "
            f"({description})"
        )


def validate_message(
    message: ParsedHL7Message,
) -> ValidationResult:
    """
    Valida uma mensagem HL7 já interpretada pelo Parser.

    O Validator não conhece MLLP, sockets ou framing.
    Sua responsabilidade é avaliar se o conteúdo recebido
    pode seguir no pipeline de processamento.
    """

    if message.message_type not in SUPPORTED_MESSAGE_TYPES:
        return ValidationResult(
            valid=False,
            ack_code="AR",
            reason="Unsupported message type",
            errors=[
                f"Unsupported message type: "
                f"{message.message_type or '<missing>'}"
            ],
        )

    errors = []

    validate_required_segment(
        message,
        "MSH",
        errors,
    )

    validate_required_segment(
        message,
        "EVN",
        errors,
    )

    validate_required_segment(
        message,
        "PID",
        errors,
    )

    validate_required_segment(
        message,
        "PV1",
        errors,
    )

    validate_required_field(
        message,
        "MSH",
        10,
        "Message Control ID",
        errors,
    )

    validate_required_field(
        message,
        "MSH",
        12,
        "HL7 Version",
        errors,
    )

    validate_required_field(
        message,
        "PID",
        3,
        "Patient Identifier",
        errors,
    )

    validate_required_field(
        message,
        "PID",
        5,
        "Patient Name",
        errors,
    )

    validate_required_field(
        message,
        "PV1",
        2,
        "Patient Class",
        errors,
    )

    validate_required_field(
        message,
        "PV1",
        19,
        "Visit Number",
        errors,
    )

    validate_required_field(
        message,
        "PV1",
        44,
        "Admit Date/Time",
        errors,
    )

    if errors:
        return ValidationResult(
            valid=False,
            ack_code="AE",
            reason="HL7 validation failed",
            errors=errors,
        )

    return ValidationResult(
        valid=True,
        ack_code="AA",
        reason="Message accepted",
        errors=[],
    )
