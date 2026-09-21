import unittest
from pathlib import Path

from src.gateway.core.hl7_parser import parse_message
from src.gateway.core.hl7_validator import validate_message
from src.gateway.transformers.adt_a01_to_fhir import (
    transform_adt_a01,
)


MESSAGES_DIR = Path("src/his-simulator/messages")


class TestADT_A01_ToFHIR(unittest.TestCase):

    def load_message(self, filename: str) -> str:
        return (
            MESSAGES_DIR / filename
        ).read_text(encoding="utf-8")

    def test_valid_adt_a01_transforms_to_patient_and_encounter(self):
        raw_message = self.load_message(
            "adt_a01.hl7"
        )

        parsed = parse_message(raw_message)
        validation = validate_message(parsed)

        self.assertTrue(validation.valid)

        result = transform_adt_a01(parsed)

        patient = result["patient"]
        encounter = result["encounter"]

        self.assertEqual(
            patient["resourceType"],
            "Patient",
        )

        self.assertEqual(
            patient["identifier"][0]["value"],
            "789012",
        )

        self.assertEqual(
            patient["name"][0]["family"],
            "SANTOS",
        )

        self.assertEqual(
            patient["name"][0]["given"][0],
            "MARINA",
        )

        self.assertEqual(
            patient["gender"],
            "female",
        )

        self.assertEqual(
            patient["birthDate"],
            "1992-08-10",
        )

        self.assertEqual(
            patient["address"][0]["city"],
            "SALVADOR",
        )

        self.assertEqual(
            patient["address"][0]["state"],
            "BA",
        )

        self.assertEqual(
            encounter["resourceType"],
            "Encounter",
        )

        self.assertEqual(
            encounter["identifier"][0]["value"],
            "VN00001",
        )

        self.assertEqual(
            encounter["status"],
            "in-progress",
        )

        self.assertEqual(
            encounter["class"]["code"],
            "IMP",
        )

        self.assertEqual(
            encounter["subject"]["reference"],
            "Patient/temporary",
        )

        self.assertEqual(
            encounter["period"]["start"],
            "2026-09-14",
        )

        self.assertEqual(
            encounter["location"][0]["location"]["display"],
            "WARD / 101 / A",
        )

    def test_traceability_uses_message_control_id(self):
        raw_message = self.load_message(
            "adt_a01.hl7"
        )

        parsed = parse_message(raw_message)

        result = transform_adt_a01(parsed)

        expected_source = (
            "urn:hl7v2:message:MSG00001"
        )

        self.assertEqual(
            result["patient"]["meta"]["source"],
            expected_source,
        )

        self.assertEqual(
            result["encounter"]["meta"]["source"],
            expected_source,
        )


if __name__ == "__main__":
    unittest.main()
