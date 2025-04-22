import json
from fastapi import APIRouter, UploadFile, File, Form, Request, Header
import shutil
import os
from typing import List

from server.utils.printer import Printer
from server.utils.redis_cache import RedisCache
from server.tasks import process_document_task
from server.utils.constants import CLIENTS_KEY

UPLOADS_PATH = "uploads"
os.makedirs(f"{UPLOADS_PATH}/images", exist_ok=True)
os.makedirs(f"{UPLOADS_PATH}/documents", exist_ok=True)
os.makedirs(f"{UPLOADS_PATH}/analysis", exist_ok=True)

router = APIRouter()
printer = Printer("ROUTES")
redis_cache = RedisCache()


@router.post("/upload/")
async def upload_files(
    images: List[UploadFile] = File([]),
    documents: List[UploadFile] = File([]),
    hashes: str = Form(...),
    client_id: str = Header(...),
):
    printer.blue(f"🖥️ Un usuario con id {client_id} acaba de subir archivos")
    parsed_hashes = json.loads(hashes)
    printer.yellow(parsed_hashes, "Parsed hashes")

    printer.yellow("🔄 Analizando archivos...")
    for image in images:
        with open(f"{UPLOADS_PATH}/images/{image.filename}", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    for document in documents:
        with open(f"{UPLOADS_PATH}/documents/{document.filename}", "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)

    for document in documents:
        # Find the hash in the hashes list
        doc_hash = next(
            (
                h.get("hash")
                for h in parsed_hashes
                if h.get("name") == document.filename
            ),
            None,
        )
        if doc_hash:

            process_document_task.delay(document.filename, doc_hash, client_id)
        else:
            printer.red("No hash found for document", document.filename)

    return {"status": "SUCCESS", "message": "Archivos subidos y en proceso de análisis"}


@router.post("/webhook/{client_id}")
async def webhook(client_id: str, request: Request):
    from server.utils.socket_server import sio

    data = await request.json()
    hash_key = data.get("hash_key", None)
    socket_id = redis_cache.hget(CLIENTS_KEY, client_id)
    if socket_id and hash_key:
        printer.green(f"Sending analysis process to {socket_id}", hash_key)
        await sio.emit(f"analysis_process_{hash_key}", data, to=socket_id)
    else:
        printer.red("No socket id found for client", client_id)

    return {"status": "success"}
