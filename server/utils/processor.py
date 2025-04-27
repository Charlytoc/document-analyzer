import os
from server.utils.pdf_reader import DocumentReader
from server.utils.printer import Printer
from server.utils.redis_cache import RedisCache
from server.utils.ai_interface import AIInterface, get_physical_context
from server.utils.image_reader import ImageReader

EXPIRATION_TIME = 60 * 60 * 24 * 30  # 30 days

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", None)
LIMIT_CHARACTERS_FOR_FILE = 50000

printer = Printer("ROUTES")
redis_cache = RedisCache()

import hashlib
import json


def generate_sentence_brief(
    document_paths: list[str], images_paths: list[str], extra: dict = {}
):
    physical_context = get_physical_context()

    use_cache = extra.get("use_cache", True)
    system_from_client = extra.get("system_prompt", None)
    ai_interface = AIInterface(
        provider=os.getenv("PROVIDER", "ollama"), api_key=os.getenv("OLLAMA_API_KEY")
    )

    system_prompt = (
        system_from_client
        or SYSTEM_PROMPT
        or """
    ### Role
    You are an incredible legal expert in Mexican law. You are will receive all the possible text from a set of documents and images, you need to analyze them, they are related to the same case. Extract the relevant information and explain the result of the sentence in a clear and concise way,  any person should understand it. Keep in mind that your main task is to write a "Sentencia Ciudadana". You will receive a set of context documents with an example of a "Sentencia Ciudadana" and some guidelines for you to follow.

    ### Context
    These files are part of the context given to execute your task, use them to comprehend your task and follow the writing guidelines explained in the files:
    ---
    {{context}}
    ---

    ### Instructions
    - Write a "Sentencia Ciudadana" using the files that will be in the user messages.
    - Your response must be ONLY in Spanish.
    - The final response should include all the relevant information from the files, don't miss any important detail.
    """
    )
    if physical_context:
        system_prompt = system_prompt.replace("{{context}}", physical_context)

    messages = [{"role": "system", "content": system_prompt}]
    document_reader = DocumentReader()

    for document_path in document_paths:
        document_text = document_reader.read(document_path)
        messages.append(
            {
                "role": "user",
                "content": f"document: {document_text[:LIMIT_CHARACTERS_FOR_FILE]}",
            }
        )

    for image_path in images_paths:
        image_reader = ImageReader()
        image_text = image_reader.read(image_path)
        messages.append(
            {
                "role": "user",
                "content": f"image: {image_text[:LIMIT_CHARACTERS_FOR_FILE]}",
            }
        )

    # Crear hash de los mensajes
    messages_json = json.dumps(messages, sort_keys=True)
    messages_hash = hashlib.sha256(messages_json.encode("utf-8")).hexdigest()

    if use_cache:
        cached_response = redis_cache.get(messages_hash)
        if cached_response:
            printer.green(f"Cache hit for hash: {messages_hash}")
            return cached_response

    # Si no existe en cache, generar nueva respuesta
    printer.red(f"Cache miss for hash: {messages_hash}")
    response = ai_interface.chat(messages=messages, model=os.getenv("MODEL", "gemma3"))

    # Guardar en cache
    redis_cache.set(messages_hash, response, ex=EXPIRATION_TIME)
    printer.green(f"Cache saved for hash: {messages_hash}")

    return response
