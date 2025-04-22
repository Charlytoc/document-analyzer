# server/socket.py
import socketio

# Register the namespace
from server.utils.socket_events import NamespaceEvents

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    transports=["websocket", "polling"],
    max_http_buffer_size=20 * 1024 * 1024,
    logger=False,
    engineio_logger=False,
)


sio.register_namespace(NamespaceEvents("/"))
