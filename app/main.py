import json
import logging
import time
from http import HTTPStatus
from os import listdir, path

# fastapi
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
from starlette.requests import Request
from starlette.responses import Response

# app
import tasks

base_dir = path.dirname(path.abspath(__file__))
log_cfg_path = path.join(base_dir, "logging.cfg")

# setup loggers
logging.config.fileConfig(log_cfg_path, disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(
    __name__
)  # the __name__ resolve to "main" since we are at the root of the project.
# This will get the root logger since no logger in the configuration has this name.

app = FastAPI()



def now_ms():
    return int(time.time_ns() / (1000 * 1000))


def since_ms(start_ms, finish_ms=None):
    if finish_ms is None:
        finish_ms = now_ms()
    return finish_ms - start_ms


"""
"""
# @app.middleware('http')
# async def catch_exceptions_middleware(request: Request, call_next):
#    try:
#        return await call_next(request)
#    except Exception as e:
#        logger.error(str(e))
#        return Response("Internal server error", status_code=500)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = now_ms() % (1000 * 1000)
    logger.info(f"rid={rid} start request path={request.url.path}")
    start_ms = now_ms()

    response = await call_next(request)

    process_ms = since_ms(start_ms)
    fmt_process_time = "{0:.2f}".format(process_ms)
    logger.info(
        f"rid={rid} completed_in={fmt_process_time}ms status_code={response.status_code}"
    )

    return response


@app.get("/alive")
async def alive():
    logger.info("alive check")
    return {"status": "alive"}


@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # 1 hour
def every_hour() -> None:
    logger.info("every_hour")


@app.get("/mosaic/{url}")
def mosaic(url, request: Request):
    qp = dict(request.query_params)
    ops = {}

    if "enlarge" in qp:
        ops["enlarge"] = int(qp["enlarge"])

    if "multi" in qp:
        ops["multi"] = float(qp["multi"])

    ops["url"] = url
    res = tasks.enqueue_mosaic_task(ops)
    uid = res.task_id
    logger.info(f"mosaic uid:{uid}")
    return {"uid": uid}


@app.get("/state/{uid}")
def state(uid):
    res = tasks.state(uid)
    return res


@app.get("/inspect")
def inspect():
    res = tasks.inspect()
    return res
