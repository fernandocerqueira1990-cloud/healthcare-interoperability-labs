from pathlib import Path
import socket
import sys


HOST = "127.0.0.1"
PORT = 2575

START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"

DEFAULT_MESSAGE_FILE = Path(
    "src/his-simulator/messages/adt_a01.hl7"
)


def frame_mllp(message: str) -> bytes:
    return (
        START_BLOCK
        + message.encode("utf-8")
        + END_BLOCK
        + CARRIAGE_RETURN
    )


def receive_mllp(sock: socket.socket) -> str:
    buffer = b""

    while True:
        chunk = sock.recv(4096)

        if not chunk:
            break

        buffer += chunk

        start = buffer.find(START_BLOCK)
        end = buffer.find(
            END_BLOCK + CARRIAGE_RETURN
        )

        if start != -1 and end != -1:
            payload = buffer[start + 1:end]
            return payload.decode("utf-8")

    raise RuntimeError(
        "Connection closed before complete MLLP message"
    )


def main():
    message_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_MESSAGE_FILE
    )

    if not message_file.exists():
        raise FileNotFoundError(
            f"Message file not found: {message_file}"
        )

    message = message_file.read_text(
        encoding="utf-8"
    )

    print("========================================")
    print(" HIS SIMULATOR - MLLP CLIENT")
    print("========================================")
    print(f"Target: {HOST}:{PORT}")
    print()
    print("Sending HL7 message...")
    print()

    with socket.create_connection(
        (HOST, PORT),
        timeout=10,
    ) as sock:
        sock.sendall(
            frame_mllp(message)
        )

        ack = receive_mllp(sock)

    print("ACK received:")
    print("----------------------------------------")
    print(
        ack.replace("\r", "\n")
    )
    print("----------------------------------------")
    print()

    if "MSA|AA|" in ack:
        print("ACK TYPE: AA - Application Accept")
        print("ACK VALIDATION RESULT: PASS")

    elif "MSA|AE|" in ack:
        print("ACK TYPE: AE - Application Error")
        print("ACK VALIDATION RESULT: PASS")

    elif "MSA|AR|" in ack:
        print("ACK TYPE: AR - Application Reject")
        print("ACK VALIDATION RESULT: PASS")

    else:
        print("ACK VALIDATION RESULT: FAIL")


if __name__ == "__main__":
    main()
