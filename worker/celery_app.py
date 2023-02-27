from celery import Celery
# Notice: redis and rabbit hosts are from docker-compose.yml not localhost!

celery_app_broker = 'pyamqp://guest@rabbit//'
celery_app_result_backend = 'redis://redis:6379/0'
# celery_app_broker = celery_app_result_backend

#
# included from both front-end-producer and backend-consumer of messages.
# These are two distinct objects that run on different machines...
#
celery_app = Celery('tasks', backend=celery_app_result_backend, broker=celery_app_broker)
