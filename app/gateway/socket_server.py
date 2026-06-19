import asyncio
import logging

from app.core.database import SessionLocal
from app.services.gateway_service import establish_session, HandshakeError

logger = logging.getLogger("qvpn.gateway")

HOST = "0.0.0.0"
PORT = 5151  # the raw VPN tunnel port -- separate from the FastAPI HTTP port


async def _read_length_prefixed(reader: asyncio.StreamReader) -> bytes:
    """
    Reads one length-prefixed field from the stream:
    first 4 bytes = big-endian length, then that many bytes of payload.

    Why this helper exists: we need this exact same 2-step read (read the
    4-byte length, then read that many bytes) for BOTH the client_identifier
    and the kem_ciphertext, so we wrote it once instead of repeating it.
    """
    length_bytes = await reader.readexactly(4)
    length = int.from_bytes(length_bytes, byteorder="big")
    payload = await reader.readexactly(length)
    return payload


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Called automatically by asyncio for each new raw TCP connection.
    Runs the handshake, then (for now) just acknowledges -- the actual
    traffic-forwarding loop after a successful handshake is a follow-up
    ticket, not part of this one.
    """
    peer_addr = writer.get_extra_info("peername")
    logger.info(f"[GATEWAY] New connection from {peer_addr}")

    db = SessionLocal()
    try:
        # Step 1: read the client's identifier and ciphertext off the wire.
        # readexactly raises IncompleteReadError if the client disconnects
        # mid-message -- we let that bubble up to the except block below.
        client_identifier_bytes = await _read_length_prefixed(reader)
        kem_ciphertext = await _read_length_prefixed(reader)

        client_identifier = client_identifier_bytes.decode("utf-8")
        logger.info(f"[GATEWAY] Handshake attempt from client_identifier={client_identifier}")

        remote_ip, remote_port = peer_addr[0], peer_addr[1]

        # Step 2: hand off to the service layer -- this is the ONLY place
        # that calls into the real crypto + database logic. The socket
        # handler itself stays "dumb" on purpose.
        result = establish_session(
            db=db,
            client_identifier=client_identifier,
            kem_ciphertext=kem_ciphertext,
            remote_ip=remote_ip,
            remote_port=remote_port,
        )

        logger.info(f"[GATEWAY] Session established: {result['session_id']}")

        # Step 3: tell the client the handshake succeeded.
        # We send back the session_id so the client can reference it later
        # (e.g. in heartbeat packets). We do NOT send the shared_secret back
        # -- the client already derived its own copy independently during
        # its own encapsulation step.
        session_id_bytes = result["session_id"].encode("utf-8")
        writer.write(len(session_id_bytes).to_bytes(4, byteorder="big"))
        writer.write(session_id_bytes)
        await writer.drain()

        # NOTE: traffic-forwarding loop goes here in a future ticket.
        # For now, the connection just closes after a successful handshake.

    except asyncio.IncompleteReadError:
        logger.warning(f"[GATEWAY] {peer_addr} disconnected mid-handshake")
    except HandshakeError as exc:
        logger.warning(f"[GATEWAY] Handshake failed for {peer_addr}: {exc}")
        writer.write(b"\x00\x00\x00\x05ERROR")
        await writer.drain()
    except Exception as exc:
        logger.exception(f"[GATEWAY] Unexpected error handling {peer_addr}: {exc}")
    finally:
        db.close()
        writer.close()
        await writer.wait_closed()
        logger.info(f"[GATEWAY] Closed connection to {peer_addr}")


async def start_gateway_server() -> asyncio.AbstractServer:
    """
    Starts the asyncio socket server. Called once from main.py's lifespan
    on app startup, and the returned server object is closed on shutdown.
    """
    server = await asyncio.start_server(handle_client, HOST, PORT)
    logger.info(f"[GATEWAY] Listening for VPN tunnel connections on {HOST}:{PORT}")
    return server