from dataclasses import dataclass

from src.gateway.clients.fhir_client import FHIRClient
from src.gateway.core.hl7_parser import parse_message
from src.gateway.core.hl7_validator import validate_message
from src.gateway.transformers.adt_a01_to_fhir import (
    build_encounter,
    build_patient,
)


@dataclass
class ADTA01Result:
    patient_id: str
    encounter_id: str


class ADTA01ProcessingError(Exception):
    pass


def process_adt_a01(
    raw_message: str,
    fhir_client: FHIRClient,
) -> ADTA01Result:
    """
    Executa o pipeline ADT^A01:

    raw HL7
        -> parse
        -> validate
        -> build Patient
        -> persist Patient
        -> build Encounter with Patient reference
        -> persist Encounter
    """

    parsed = parse_message(raw_message)

    validation = validate_message(parsed)

    if not validation.valid:
        raise ADTA01ProcessingError(
            (
                f"HL7 validation failed: "
                f"{validation.ack_code} - "
                f"{validation.reason} - "
                f"{validation.errors}"
            )
        )

    patient = build_patient(parsed)

    patient_response = (
        fhir_client.create_resource(
            patient
        )
    )

    patient_reference = (
        f"Patient/"
        f"{patient_response.resource_id}"
    )

    encounter = build_encounter(
        parsed,
        patient_reference=patient_reference,
    )

    encounter_response = (
        fhir_client.create_resource(
            encounter
        )
    )

    return ADTA01Result(
        patient_id=(
            patient_response.resource_id
        ),
        encounter_id=(
            encounter_response.resource_id
        ),
    )
