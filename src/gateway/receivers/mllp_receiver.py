import logging
import os
import re
import socket
from datetime import datetime


HOST = os.getenv("MLLP_HOST", "127.0.0.1")
PORT = int(os.getenv("MLLP_PORT", "2575"))

START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("mllp-receiver")


def frame_mllp(message: str) -> bytes:
    return (
        START_BLOCK
        + message.encode("utf-8")
        + END_BLOCK
        + CARRIAGE_RETURN
    )


def extract_mllp_message(buffer: bytes):
    start = buffer.find(START_BLOCK)

    if start == -1:
        return None, buffer

    end = buffer.find(
        END_BLOCK + CARRIAGE_RETURN,
        start + 1,
    )

    if end == -1:
        return None, buffer

    payload = buffer[start + 1:end]
    remaining_buffer = buffer[
        end + len(END_BLOCK + CARRIAGE_RETURN):
    ]

    message = payload.decode("utf-8")

    return message, remaining_buffer


def get_msh_segment(message: str):
    segments = re.split(r"\r\n|\r|\n", message)

    for segment in segments:
        if segment.startswith("MSH"):
            return segment

    raise ValueError("MSH segment not found")


def parse_msh(message: str):
    msh = get_msh_segment(message)

    if len(msh) < 4:
        raise ValueError("Invalid MSH segment")

    field_separator = msh[3]
    fields = msh.split(field_separator)

    if len(fields) < 12:
        raise ValueError("Incomplete MSH segment")

    return {
        "field_separator": field_separator,
        "encoding_characters": fields[1],
        "sending_application": fields[2],
        "sending_facility": fields[3],
        "receiving_application": fields[4],
        "receiving_facility": fields[5],
        "message_type": fields[8],
        "message_control_id": fields[9],
        "processing_id": fields[10],
        "version": fields[11],
    }


def build_ack(
    original_message: str,
    acknowledgement_code: str = "AA",
    acknowledgement_text: str = "Message accepted",
):
    metadata = parse_msh(original_message)

    separator = metadata["field_separator"]
    message_type = metadata["message_type"]
    message_control_id = metadata["message_control_id"]

    trigger_event = ""

    if "^" in message_type:
        parts = message_type.split("^")

        if len(parts) > 1:
            trigger_event = parts[1]

    ack_message_type = (
        f"ACK^{trigger_event}"
        if trigger_event
        else "ACK"
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    ack_control_id = "ACK" + datetime.now().strftime("%Y%m%d%H%M%S%f")

    msh_fields = [
        "MSH",
        metadata["encoding_characters"],
        metadata["receiving_application"],
        metadata["receiving_facility"],
        metadata["sending_application"],
        metadata["sending_facility"],
        timestamp,
        "",
        ack_message_type,
        ack_control_id,
        metadata["processing_id"],
        metadata["version"],
    ]

    msh = separator.join(msh_fields)

    msa_fields = [
        "MSA",
        acknowledgement_code,
        message_control_id,
        acknowledgement_text,
    ]

    msa = separator.join(msa_fields)

    return f"{msh}\r{msa}\r"


def handle_message(message: str):
    metadata = parse_msh(message)

    message_type = metadata["message_type"]
    message_control_id = metadata["message_control_id"]

    logger.info(
        "HL7 received | type=%s | control_id=%s",
        message_type,
        message_control_id or "<missing>",
    )

    if not message_control_id:
        logger.error(
            "HL7 validation failed | reason=missing MSH-10"
        )

        ack = build_ack(
            original_message=message,
            acknowledgement_code="AE",
            acknowledgement_text="Missing Message Control ID",
        )

        logger.info(
            "ACK generated | code=AE | correlation_id=<missing>"
        )

        return ack

    if message_type != "ADT^A01":
        logger.error(
            "HL7 rejected | reason=unsupported message type | type=%s",
            message_type,
        )

        ack = build_ack(
            original_message=message,
            acknowledgement_code="AR",
            acknowledgement_text="Unsupported message type",
        )

        logger.info(
            "ACK generated | code=AR | correlation_id=%s",
            message_control_id,
        )

        return ack

    ack = build_ack(
        original_message=message,
        acknowledgement_code="AA",
        acknowledgement_text="Message accepted",
    )

    logger.info(
        "ACK generated | code=AA | correlation_id=%s",
        message_control_id,
    )

    return ack


def run_server():
    logger.info(
        "Starting MLLP Receiver on %s:%s",
        HOST,
        PORT,
    )

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as server:
        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        server.bind((HOST, PORT))
        server.listen()

        logger.info(
            "MLLP Receiver listening on %s:%s",
            HOST,
            PORT,
        )

        while True:
            connection, address = server.accept()

            logger.info(
                "Connection opened | client=%s:%s",
                address[0],
                address[1],
            )

            with connection:
                buffer = b""

                while True:
                    chunk = connection.recv(4096)

                    if not chunk:
                        break

                    buffer += chunk

                    while True:
                        message, buffer = extract_mllp_message(buffer)

                        if message is None:
                            break

                        try:
                            ack = handle_message(message)
                            connection.sendall(frame_mllp(ack))

                        except Exception as exc:
                            logger.exception(
                                "Message processing failed: %s",
                                exc,
                            )

            logger.info(
                "Connection closed | client=%s:%s",
                address[0],
                address[1],
            )


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("MLLP Receiver stopped")
