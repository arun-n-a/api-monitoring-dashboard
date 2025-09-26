import os
import ssl
import asyncio

from requests.exceptions import RequestException
from celery import Celery
from celery.exceptions import MaxRetriesExceededError
# from asgiref.sync import async_to_sync
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.services.open_ai import (
    ai_completion_call_redis_status_set, 
    ai_completion_call)


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", settings.REDIS_URL)
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", settings.REDIS_URL)

celery.conf.broker_use_ssl = {
    'ssl_cert_reqs': ssl.CERT_NONE,
    'ssl_check_hostname': False
}

celery.conf.enable_utc = True
celery.conf.timezone = 'UTC'
celery.conf.event_queue_ttl = 60
celery.conf.event_queue_expires = 120


# @celery.task(
#     bind=True,
#     autoretry_for=(Exception,),
#     retry_backoff=True,       # exponential backoff
#     retry_backoff_max=600,    # max wait between retries (optional)
#     retry_jitter=True,        # add randomness (good for load)
#     max_retries=5
# )
