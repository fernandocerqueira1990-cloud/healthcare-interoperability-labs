from typing import Dict

from src.gateway.core.hl7_parser import ParsedHL7Message


PATIENT_CLASS_MAP = {
    "I": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "IMP",
        "display": "inpatient encounter",
    },
    "O": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "AMB",
        "display": "ambulatory",
    },
    "E": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "EMER",
        "display": "emergency",
    },
}


def component(
    value: str,
    position: int,
    separator: str = "^",
) -> str:
    """
    Retorna um componente HL7 utilizando posição baseada em 1.

    Exemplo:
        SANTOS^MARINA
        component(value, 1) -> SANTOS
        component(value, 2) -> MARINA
    """
    if not value:
        return ""

    parts = value.split(separator)

    index = position - 1

    if index >= len(parts):
        return ""

    return parts[index]


def hl7_date_to_fhir(value: str) -> str:
    """
    Converte YYYYMMDD para YYYY-MM-DD.
    """
    if not value or len(value) < 8:
        return ""

    return (
        f"{value[0:4]}-"
        f"{value[4:6]}-"
        f"{value[6:8]}"
    )


def hl7_datetime_to_fhir_date(value: str) -> str:
    """
    Neste milestone preservamos apenas a parte da data.

    O timestamp HL7 de exemplo não possui timezone.
    Para não inventar informação temporal que não existe
    na origem, não adicionamos offset artificialmente.
    """
    return hl7_date_to_fhir(value)


def map_gender(value: str) -> str:
    mapping = {
        "M": "male",
        "F": "female",
        "O": "other",
        "U": "unknown",
    }

    return mapping.get(value, "unknown")


def build_patient(
    message: ParsedHL7Message,
) -> Dict:
    pid = message.segments["PID"]

    identifier = pid.get(3, "")
    name = pid.get(5, "")
    address = pid.get(11, "")
    phone = pid.get(13, "")

    patient = {
        "resourceType": "Patient",
        "meta": {
            "source": (
                f"urn:hl7v2:message:"
                f"{message.message_control_id}"
            )
        },
        "identifier": [
            {
                "system": (
                    "urn:healthcare-interoperability-labs:"
                    "patient-id"
                ),
                "value": component(identifier, 1),
            }
        ],
        "name": [
            {
                "family": component(name, 1),
                "given": [
                    component(name, 2)
                ],
            }
        ],
        "gender": map_gender(
            pid.get(8, "")
        ),
        "birthDate": hl7_date_to_fhir(
            pid.get(7, "")
        ),
    }

    if address:
        patient["address"] = [
            {
                "line": [
                    component(address, 1)
                ],
                "city": component(address, 3),
                "state": component(address, 4),
                "postalCode": component(address, 5),
                "country": component(address, 6),
            }
        ]

    if phone:
        patient["telecom"] = [
            {
                "system": "phone",
                "value": phone,
            }
        ]

    return patient


def build_encounter(
    message: ParsedHL7Message,
    patient_reference: str = "Patient/temporary",
) -> Dict:
    pv1 = message.segments["PV1"]

    patient_class = pv1.get(2, "")
    location = pv1.get(3, "")

    encounter_class = PATIENT_CLASS_MAP.get(
        patient_class,
        {
            "system": (
                "http://terminology.hl7.org/"
                "CodeSystem/v3-ActCode"
            ),
            "code": "AMB",
            "display": "ambulatory",
        },
    )

    encounter = {
        "resourceType": "Encounter",
        "meta": {
            "source": (
                f"urn:hl7v2:message:"
                f"{message.message_control_id}"
            )
        },
        "identifier": [
            {
                "system": (
                    "urn:healthcare-interoperability-labs:"
                    "visit-number"
                ),
                "value": pv1.get(19, ""),
            }
        ],
        "status": "in-progress",
        "class": encounter_class,
        "subject": {
            "reference": patient_reference,
        },
        "period": {
            "start": hl7_datetime_to_fhir_date(
                pv1.get(44, "")
            )
        },
    }

    if location:
        location_display = " / ".join(
            part
            for part in location.split("^")
            if part
        )

        encounter["location"] = [
            {
                "location": {
                    "display": location_display,
                }
            }
        ]

    return encounter


def transform_adt_a01(
    message: ParsedHL7Message,
) -> Dict:
    """
    Transforma ADT^A01 validado em recursos FHIR R4.

    Gera Patient e Encounter em memória para testes e uso
    isolado do transformer. No fluxo end-to-end, o service
    persiste o Patient primeiro e reconstrói o Encounter com
    a referência FHIR real do Patient.
    """
    patient = build_patient(message)

    encounter = build_encounter(message)

    return {
        "patient": patient,
        "encounter": encounter,
    }
