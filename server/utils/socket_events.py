import socketio
import json
from .printer import Printer
from .redis_cache import RedisCache
from .ai_interface import AIInterface
import os
from dotenv import load_dotenv
from .constants import CLIENTS_KEY

load_dotenv()

printer = Printer("SOCKET EVENTS")
redis_cache = RedisCache()
EXPIRATION_TIME = 60 * 60 * 24 * 30

MAX_CHARACTERS_FOR_ANALYSIS = 50000


class NamespaceEvents(socketio.AsyncNamespace):

    def on_connect(self, sid, environ):
        print("CONNECTED TO SOCKET")
        # on_connect_handler(socket_id=sid)

    def on_register_client(self, sid, data):
        from .socket_server import sio

        client_id = data.get("client_id", None)
        redis_cache.hset(CLIENTS_KEY, client_id, sid)

    async def on_message(self, sid, data):
        from .socket_server import sio

        ai_interface = AIInterface(
            provider=os.getenv("PROVIDER", "openai"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        client_id = data.get("client_id", None)
        files = data.get("files", None)
        messages = data.get("messages", None)
        prompt = data.get("prompt", None)

        if not client_id or not prompt:
            printer.red("The client id or prompt is not valid")
            return

        all_documents_text = ""

        for file in files:
            doc = redis_cache.get(file.get("hash"))
            doc = json.loads(doc)
            all_documents_text += f"""
<document name="{file.get('name', '')}">
<analysis desc="This is a previous analysis an AI made of the document, it may be incomplete or incorrect, you can use it in your response if needed">
    {doc.get("analysis", "")}
</analysis>
<text desc="This is the text of the document">
    {doc.get("text", "")[:MAX_CHARACTERS_FOR_ANALYSIS]}
</text>
</document>
"""

        messages = [
            {
                "role": "system",
                "content": f"""You are a legal expert in Mexican law.

                You are given a question and a set of documents.
                Your task is to answer the question using the information provided in the documents.

                ### RULES
                - Your response must be only in Spanish.
                - You should use a natural language, not a legal language.
                - You should answer the question based on the information provided in the documents. If you don't have enough information, say that you don't know because you don't have enough information.
                - Be as specific as possible.
                - Think before giving your response, don't rush.
                
                
                ---
                {all_documents_text[:MAX_CHARACTERS_FOR_ANALYSIS]}
                ---
                """,
            },
            *messages,
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = ai_interface.chat(
            messages=messages,
            model=os.getenv("MODEL", "gpt-4o-mini"),
        )

        await sio.emit("message_response", {"message": response}, to=sid)

    def on_disconnect(self, sid):

        print("DISCONNECTED FROM SOCKET")
