import celery.states
from celery.result import AsyncResult
from worker.celery_app import celery_app

import logging

logger = logging.getLogger(
    __name__
)  # the __name__ resolve to "main" since we are at the root of the project.
# This will get the root logger since no logger in the configuration has this name.

# Create the celery app and get the logger
# celery_app = Celery('tasks', backend='rpc://',broker='pyamqp://guest@rabbit//')


def state(uid):
    res = AsyncResult(app=celery_app, id=uid)
    if res.state == celery.states.SUCCESS:
        rc = {"state": celery.states.SUCCESS, "result": res.result}
    elif res.state == "PROGRESS":
        rc = {"state": "PROGRESS", "info": res.info}
    elif res.state == celery.states.PENDING:
        rc = {"state": "UNKNOWNN"}
    else:
        rc = {"state": res.state}

    return rc


def inspect():
    res = celery_app.control.inspect().active()
    return res


def enqueue_mosaic_task(ops):
    res = celery_app.send_task("worker.tasks.mosaic_task", args=[ops])
    # res = worker.tasks.mosaic_task.delay(ops)
    return res
