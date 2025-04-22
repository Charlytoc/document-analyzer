To run celery worker:

<!-- # celery -A server.celery_app worker --loglevel=info --pool=solo  -->

```bash
 celery -A server.celery_app worker --loglevel=info --pool=gevent
```

To run FastAPI server:

```bash
uvicorn main:app --reload
```

To run a Redis container:

```bash
docker run -d --name document_redis -p 6380:6379 redis
```
