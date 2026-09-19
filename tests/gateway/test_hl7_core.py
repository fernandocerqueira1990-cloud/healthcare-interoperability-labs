import unittest
from pathlib import Path

from src.gateway.core.hl7_parser import parse_message
from src.gateway.core.hl7_validator import validate_message


MESSAGES_DIR = Path("src/his-simulator/messages")


class TestHL7ParserAndValidator(unittest.TestCase):

    def load_message(self, filename: str) -> str:
        return (
            MESSAGES_DIR / filename
        ).read_text(encoding="utf-8")

    def test_valid_adt_a01_returns_aa(self):
        raw_message = self.load_message(
            "adt_a01.hl7"
        )

        parsed = parse_message(raw_message)
        result = validate_message(parsed)

        self.assertEqual(
            parsed.message_type,
            "ADT^A01",
        )

        self.assertEqual(
            parsed.trigger_event,
            "A01",
        )

        self.assertEqual(
            parsed.message_control_id,
            "MSG00001",
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.ack_code, "AA")
        self.assertEqual(
            result.reason,
            "Message accepted",
        )

        self.assertEqual(
            result.errors,
            [],
        )

    def test_missing_control_id_returns_ae(self):
        raw_message = self.load_message(
            "adt_a01_invalid.hl7"
        )

        parsed = parse_message(raw_message)
        result = validate_message(parsed)

        self.assertEqual(
            parsed.message_type,
            "ADT^A01",
        )

        self.assertEqual(
            parsed.message_control_id,
            "",
        )

        self.assertFalse(result.valid)
        self.assertEqual(result.ack_code, "AE")

        self.assertIn(
            (
                "Missing required field: "
                "MSH-10 (Message Control ID)"
            ),
            result.errors,
        )

    def test_unsupported_message_returns_ar(self):
        raw_message = self.load_message(
            "orm_o01_unsupported.hl7"
        )

        parsed = parse_message(raw_message)
        result = validate_message(parsed)

        self.assertEqual(
            parsed.message_type,
            "ORM^O01",
        )

        self.assertFalse(result.valid)
        self.assertEqual(result.ack_code, "AR")

        self.assertEqual(
            result.reason,
            "Unsupported message type",
        )

        self.assertIn(
            "Unsupported message type: ORM^O01",
            result.errors,
        )

    def test_parser_exposes_expected_segments(self):
        raw_message = self.load_message(
            "adt_a01.hl7"
        )

        parsed = parse_message(raw_message)

        self.assertIn("MSH", parsed.segments)
        self.assertIn("EVN", parsed.segments)
        self.assertIn("PID", parsed.segments)
        self.assertIn("PV1", parsed.segments)

    def test_empty_message_raises_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "HL7 message is empty",
        ):
            parse_message("")

    def test_message_without_msh_raises_error(self):
        invalid_message = (
            "PID|1||PAT001||DOE^JOHN\r"
            "PV1|1|I\r"
        )

        with self.assertRaisesRegex(
            ValueError,
            "MSH segment not found",
        ):
            parse_message(invalid_message)


if __name__ == "__main__":
    unittest.main()
