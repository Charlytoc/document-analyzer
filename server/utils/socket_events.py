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
    # user_id_to_socket_id = {}
    # socket_id_to_user_id = {}

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
            provider="openai", api_key=os.getenv("OPENAI_API_KEY")
        )
        client_id = data.get("client_id", None)
        files = data.get("files", None)
        messages = data.get("messages", None)
        prompt = data.get("prompt", None)

        if not client_id or not prompt:
            printer.red("The client id or prompt is not valid")
            return

        # if not redis_cache.exists(client_id):
        #     printer.red("The client id does not exist in the redis cache")
        #     return

        # saved_context = json.loads(redis_cache.get(client_id) or "{}")

        # if not saved_context:
        #     printer.red("The client id does not exist in the redis cache")
        #     return

        # printer.blue(saved_context, "SAVED CONTEXT")
        all_documents_text = ""
        # Recorrer todas las keys de saved_context
        # for key in saved_context.keys():
        #     if key == "client_id":
        #         continue

        #             all_documents_text += f"""
        # <document name="{saved_context[key].get('filename', '')}">
        #     {saved_context[key].get('text', '')}
        # </document>
        # """
        for file in files:
            doc = redis_cache.get(file.get("hash"))
            doc = json.loads(doc)
            all_documents_text += f"""
<document name="{file.get('name', '')}">
    {doc.get("analysis", "") or doc.get("text", "")}
</document>
"""

        messages = [
            {
                "role": "system",
                "content": f"""You are a legal expert in Mexican law.

                You are given a question and a set of documents.
                Your task is to answer the question using the information provided in the documents.

                The documents are:
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
            model="gpt-4o-mini",
        )

        await sio.emit("message_response", {"message": response}, to=sid)

    # async def on_listen_analysis(self, sid, job_id):
    #     from .socket_server import sio

    #     printer.blue("An user wants to listen the analysis of a document")

    #     if redis_cache.exists(job_id):
    #         printer.blue("The job id exists in the redis cache")
    #         saved_context = json.loads(redis_cache.get(job_id) or "{}")
    #         saved_context["client_id"] = sid

    #         redis_cache.set(
    #             job_id, json.dumps(saved_context).encode("utf-8"), EXPIRATION_TIME
    #         )
    #         await sio.emit("analysis_response", saved_context, to=sid)
    #     else:
    #         printer.blue("The job id does not exist in the redis cache")

    #     return job_id

    def on_disconnect(self, sid):

        print("DISCONNECTED FROM SOCKET")
        # on_disconnect_handler(socket_id=sid)
