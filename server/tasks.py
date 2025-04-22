from .celery_app import celery_app
from .utils.processor import process_document


@celery_app.task()
def process_document_task(
    filename: str,
    doc_hash: str,
    client_id: str,
):
    process_document(
        filename=filename,
        client_id=client_id,
        use_cache=False,
        doc_hash=doc_hash,
    )
    return "File analyzed and result saved in Redis"
