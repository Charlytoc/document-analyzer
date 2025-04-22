import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import socketio
from contextlib import asynccontextmanager
from server.utils.ai_interface import check_ollama_installation
from server.utils.printer import Printer
from fastapi.middleware.cors import CORSMiddleware

from server.routes import router
from server.utils.socket_server import sio

printer = Printer("MAIN")


@asynccontextmanager
async def lifespan(app: FastAPI):
    printer.yellow("Checking ollama installation")
    result = check_ollama_installation()
    if result["installed"]:
        printer.green("Ollama is installed")
        printer.green("Ollama version: ", result["version"])
        printer.green("Ollama server running: ", result["server_running"])

    else:
        printer.red("Ollama is not installed")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

app.add_route("/socket.io/", route=sio_asgi_app, methods=["GET", "POST"])
app.add_websocket_route("/socket.io/", route=sio_asgi_app)

app.mount("/client", StaticFiles(directory="client/dist", html=True), name="client")

os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/documents", exist_ok=True)

UPLOADS_PATH = "uploads"
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
