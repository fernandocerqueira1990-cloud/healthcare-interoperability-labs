from pathlib import Path

MESSAGE_FILE = Path("src/his-simulator/messages/adt_a01.hl7")


def parse_message(content: str):
    segments = {}

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        segment_name = line[:3]

        if segment_name == "MSH":
            separator = line[3]
            raw_fields = line.split(separator)
            fields = {1: separator}

            for index, value in enumerate(raw_fields[1:], start=2):
                fields[index] = value
        else:
            raw_fields = line.split("|")
            fields = {
                index: value
                for index, value in enumerate(raw_fields[1:], start=1)
            }

        segments[segment_name] = fields

    return segments


def validate_required_segment(segments, name):
    if name not in segments:
        print(f"[ERROR] Segmento {name} não encontrado")
        return False

    print(f"[OK] Segmento {name} encontrado")
    return True


def validate_field(segments, segment, field, description):
    value = segments.get(segment, {}).get(field, "")

    if not value:
        print(f"[ERROR] {segment}-{field} ({description}) vazio ou ausente")
        return False

    print(f"[OK] {segment}-{field} ({description}) = {value}")
    return True


def main():
    if not MESSAGE_FILE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {MESSAGE_FILE}")

    content = MESSAGE_FILE.read_text(encoding="utf-8")
    segments = parse_message(content)

    print("========================================")
    print(" HL7 ADT^A01 STRUCTURAL VALIDATION")
    print("========================================")

    checks = []

    checks.append(validate_required_segment(segments, "MSH"))
    checks.append(validate_required_segment(segments, "EVN"))
    checks.append(validate_required_segment(segments, "PID"))
    checks.append(validate_required_segment(segments, "PV1"))

    print()

    checks.append(validate_field(segments, "MSH", 9, "Message Type"))
    checks.append(validate_field(segments, "MSH", 10, "Message Control ID"))
    checks.append(validate_field(segments, "MSH", 12, "HL7 Version"))

    print()

    checks.append(validate_field(segments, "PID", 3, "Patient Identifier"))
    checks.append(validate_field(segments, "PID", 5, "Patient Name"))

    print()

    checks.append(validate_field(segments, "PV1", 2, "Patient Class"))
    checks.append(validate_field(segments, "PV1", 19, "Visit Number"))
    checks.append(validate_field(segments, "PV1", 44, "Admit Date/Time"))

    print()

    message_type = segments.get("MSH", {}).get(9)

    if message_type == "ADT^A01":
        print("[OK] Message Type esperado: ADT^A01")
        checks.append(True)
    else:
        print(
            f"[ERROR] Message Type inválido. "
            f"Esperado ADT^A01, recebido: {message_type}"
        )
        checks.append(False)

    print()
    print("========================================")

    if all(checks):
        print("VALIDATION RESULT: PASS")
    else:
        print("VALIDATION RESULT: FAIL")

    print("========================================")


if __name__ == "__main__":
    main()
