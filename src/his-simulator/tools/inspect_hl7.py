from pathlib import Path

MESSAGE_FILE = Path("src/his-simulator/messages/adt_a01.hl7")


def inspect_segment(segment: str):
    segment = segment.rstrip("\n")
    segment_name = segment[:3]

    print(f"\n=== {segment_name} ===")

    if segment_name == "MSH":
        field_separator = segment[3]
        fields = segment.split(field_separator)

        print(f"MSH-1: {field_separator}")

        for index, value in enumerate(fields[1:], start=2):
            if value:
                print(f"MSH-{index}: {value}")

    else:
        fields = segment.split("|")

        for index, value in enumerate(fields[1:], start=1):
            if value:
                print(f"{segment_name}-{index}: {value}")


def main():
    if not MESSAGE_FILE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {MESSAGE_FILE}")

    content = MESSAGE_FILE.read_text(encoding="utf-8")
    print(f"Arquivo: {MESSAGE_FILE}")

    for line in content.splitlines():
        if line.strip():
            inspect_segment(line)


if __name__ == "__main__":
    main()
