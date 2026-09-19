import logging
import os
import socket
from datetime import datetime

from src.gateway.core.hl7_parser import parse_message
from src.gateway.core.hl7_validator import validate_message


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


def build_ack(
    parsed_message,
    acknowledgement_code: str = "AA",
    acknowledgement_text: str = "Message accepted",
):
    msh = parsed_message.segments["MSH"]

    separator = msh.get(1, "|")
    encoding_characters = msh.get(2, "^~\\&")

    sending_application = msh.get(3, "")
    sending_facility = msh.get(4, "")
    receiving_application = msh.get(5, "")
    receiving_facility = msh.get(6, "")

    trigger_event = parsed_message.trigger_event

    ack_message_type = (
        f"ACK^{trigger_event}"
        if trigger_event
        else "ACK"
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    ack_control_id = (
        "ACK"
        + datetime.now().strftime("%Y%m%d%H%M%S%f")
    )

    msh_fields = [
        "MSH",
        encoding_characters,
        receiving_application,
        receiving_facility,
        sending_application,
        sending_facility,
        timestamp,
        "",
        ack_message_type,
        ack_control_id,
        parsed_message.processing_id,
        parsed_message.version_id,
    ]

    ack_msh = separator.join(msh_fields)

    msa_fields = [
        "MSA",
        acknowledgement_code,
        parsed_message.message_control_id,
        acknowledgement_text,
    ]

    msa = separator.join(msa_fields)

    return f"{ack_msh}\r{msa}\r"


def handle_message(message: str):
    parsed = parse_message(message)

    logger.info(
        "HL7 received | type=%s | control_id=%s",
        parsed.message_type or "<missing>",
        parsed.message_control_id or "<missing>",
    )

    validation = validate_message(parsed)

    if validation.errors:
        for error in validation.errors:
            logger.error(
                "HL7 validation error | %s",
                error,
            )

    ack = build_ack(
        parsed_message=parsed,
        acknowledgement_code=validation.ack_code,
        acknowledgement_text=validation.reason,
    )

    logger.info(
        "ACK generated | code=%s | correlation_id=%s",
        validation.ack_code,
        parsed.message_control_id or "<missing>",
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
