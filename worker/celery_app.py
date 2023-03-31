from celery import Celery

# from celery.utils.log import get_task_logger

from os import getenv

# Notice: redis and rabbit hosts are from docker-compose.yml not localhost!
celery_app_broker = getenv("CELERY_BROKER_URL", "pyamqp://guest@rabbit//")
celery_app_result_backend = getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

# Create the celery app and get the logger
# logger = get_task_logger(__name__)

# logger.info(f'celery_app_broker : {celery_app_broker}')
# logger.info(f'celery_app_result_backend : {celery_app_result_backend}')

# celery_app_broker = 'pyamqp://guest@rabbit//'
# celery_app_result_backend = 'redis://redis:6379/0'
# celery_app_broker = celery_app_result_backend
# print(f'celery_app({celery_app_broker},{celery_app_result_backend})')

#
# included from both front-end-producer and backend-consumer of messages.
# These are two distinct objects that run on different machines...
#
celery_app = Celery(
    "tasks", backend=celery_app_result_backend, broker=celery_app_broker
)
