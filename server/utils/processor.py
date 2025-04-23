import os
import json
import requests
from server.utils.pdf_reader import PDFReader
from server.utils.printer import Printer
from server.utils.redis_cache import RedisCache
from server.utils.ai_interface import AIInterface
from server.utils.constants import UPLOADS_PATH

EXPIRATION_TIME = 60 * 60 * 24 * 30  # 30 days
BATCH_SIZE = os.getenv("BATCH_SIZE", 12500)

printer = Printer("ROUTES")
redis_cache = RedisCache()
ai_interface = AIInterface(
    provider=os.getenv("PROVIDER", "openai"), api_key=os.getenv("OPENAI_API_KEY")
)


def notify_client(
    client_id: str, analysis: str, doc_hash: str, percentage: int, done: bool
):
    if client_id:
        requests.post(
            f"http://localhost:8005/webhook/{client_id}",
            json={
                "hash_key": doc_hash,
                "analysis": analysis,
                "percentage": percentage,
                "done": done,
            },
        )


def process_document(
    filename: str, doc_hash: str, client_id: str, use_cache: bool = True
) -> tuple[str, str]:

    if use_cache and redis_cache.exists(doc_hash):
        document = redis_cache.get(doc_hash)
        document = json.loads(document)
        text = document.get("text", "")
        analysis = document.get("analysis", "")
        notify_client(client_id, analysis, doc_hash, 100, True)
        printer.green(f"Documento {filename} cargado desde caché")
        return text, analysis

    else:
        printer.yellow("Caché inactivo, analizando documento...")
        pdf_reader = PDFReader(engine="pymupdf")
        document_text = pdf_reader.read(f"{UPLOADS_PATH}/documents/{filename}")
        doc = {
            "text": document_text,
            "analysis": "",
        }
        redis_cache.set(doc_hash, json.dumps(doc), EXPIRATION_TIME)
        document_analysis = analize_text_in_batches(
            text=document_text,
            batch_size=BATCH_SIZE,
            client_id=client_id,
            doc_hash=doc_hash,
        )
        doc["analysis"] = "\n".join(document_analysis)
        redis_cache.set(doc_hash, json.dumps(doc), EXPIRATION_TIME)

        printer.green("Documento guardado en el caché")
        return document_text, "\n".join(document_analysis)


def analize_text_in_batches(
    text: str, batch_size: int = BATCH_SIZE, client_id: str = None, doc_hash: str = None
):
    printer.yellow(
        f"Iniciando análisis de texto con tamaño de batch {batch_size} palabras y 20% de superposición"
    )
    document_analysis = []
    words = text.split()
    overlap = max(1, int(batch_size * 0.2))
    step = batch_size - overlap
    total_words = len(words)

    for start in range(0, total_words, step):
        end = min(start + batch_size, total_words)
        batch_words = words[start:end]
        batch_text = " ".join(batch_words)
        analysis = analize_document_section(batch_text, document_analysis)

        document_analysis.append(
            f"""```analysis "This analysis is from the word {start} to the word {end}"
{start}-{end}
```
{analysis}
"""
        )

        percentage_done = round(min(100, (end / total_words) * 100), 2)
        is_last = end == total_words

        printer.blue(f"Batch {start}-{end} analyzed {percentage_done}%")

        notify_client(
            client_id,
            "".join(document_analysis),
            doc_hash,
            percentage_done,
            is_last,
        )

    printer.green(f"Todos los batches del documento {doc_hash} analizados")
    return document_analysis


faq = """
- ¿Cual fue el resultado de la demanda?
- Explícame en pocas palabras el caso.
- ¿Quién ganó la demanda?
- ¿Quién o quiénes son los quejosos del caso?
- ¿En qué leyes se basa el resultado?
- ¿Qué dice el documento con respecto a la pena impuesta?

"""


def analize_document_section(batch_text: str, previous_analysis: list[str] = []):
    # physical_context = get_physical_context()

    prompt = f"""
    <SYSTEM_PROMPT>
    <ROLE>
    You are an incredible legal expert in Mexican law. You are given a text from a legal document and you need to analyze it, extract the relevant information and explain the result of the sentence in a clear and concise way. So that any person can understand it.
    </ROLE>

    <TASK>
    The text you'll read is part of a bigger document related to a legal case. Your task is to analyze the text, extract the relevant information and explain the result of the sentence in a clear and concise way. So that any person can understand it.
    </TASK>

    <FAQ>
    These are some example questions an user may ask:
    {faq}
    </FAQ>


    <INSTRUCTIONS>
    - Extract all the relevant information from the given text, such as but not limited to: names of important people, objectives of the sentence, results, legal references, quantities (for example taxes, damages), testimonies, etc.
    - Be as precise as possible with laws, names of important people, objective of the sentence, results, etc.
    - Try to answer the questions in the FAQ using the available context if possible.
    - Continue from the previous analysis, don't start from scratch. We will concatenate your response with the previous analysis.
    - Your response must be in Spanish.
    </INSTRUCTIONS>

    """
    messages = [
        {"role": "system", "content": prompt},
        *[{"role": "assistant", "content": a} for a in previous_analysis],
        {"role": "user", "content": batch_text},
    ]

    response = ai_interface.chat(
        messages=messages, model=os.getenv("MODEL", "gpt-4o-mini")
    )

    return response
