web: gunicorn --bind 0.0.0.0:$PORT -w 2 -k uvicorn.workers.UvicornWorker app.main:app
worker: celery -A app.tasks worker -c 1 --loglevel=info --max-tasks-per-child=2