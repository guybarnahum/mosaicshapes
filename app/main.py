# Http
from http import HTTPStatus
from starlette.requests import Request
from starlette.responses import Response
import json

# misc utils
from os import path
from util import *

# fastapi
from fastapi import BackgroundTasks
from fastapi import FastAPI

from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
import logging

# app
from run import run,run_defaults
from jobs import *

base_dir = path.dirname(path.abspath(__file__))
log_cfg_path = path.join(base_dir, 'logging.cfg')

#setup loggers
logging.config.fileConfig(log_cfg_path, disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__) # the __name__ resolve to "main" since we are at the root of the project. 
                                     # This will get the root logger since no logger in the configuration has this name.

app = FastAPI()
jobs = Jobs()

'''
'''
#@app.middleware('http')
#async def catch_exceptions_middleware(request: Request, call_next):
#    try:
#        return await call_next(request)
#    except Exception as e:
#        logger.error(str(e))
#        return Response("Internal server error", status_code=500)

@app.middleware('http')
async def log_requests(request: Request, call_next):

    rid = now_ms() % (1000 * 1000)
    logger.info(f"rid={rid} start request path={request.url.path}")
    start_ms = now_ms()
    
    response = await call_next(request)
    
    process_ms = since_ms(start_ms)
    fmt_process_time = '{0:.2f}'.format(process_ms)
    logger.info(f"rid={rid} completed_in={fmt_process_time}ms status_code={response.status_code}")
    
    return response

@app.get("/alive")
async def alive():
    logger.info("alive check")
    return {'status': 'alive'}

#post
@app.get("/exec/{url}", status_code=HTTPStatus.ACCEPTED)
async def task_handler(url: str, background_tasks: BackgroundTasks):
    job = JobCreateMosaic()
    job.args['url'] = url
    background_tasks.add_task(jobs.start_job, job )
    return job

@app.get("/job-status/{uid}")
async def job_status_handler(uid: str):
    try:
        rc = jobs.get_job(uid)
    except Exception as e:
        rc = Response(str(e), status_code=400)
    return rc

@app.get("/job-list/")
async def job_list_handler():
    #all = jobs.all()
    #js = json.dumps(all, indent=4, default=json_job_serializer)
    js = jobs.toJSON()
    print(js)
    return Response(js, status_code=200)

@app.get("/job-delete/{uid}")
async def job_delete_handler(uid: str):
    try:
        jobs.purge(uid)
        rc = uid
    except Exception as e:
        rc = Response(str(e), status_code=400)
    return rc

@app.on_event("startup")
async def startup_event():
    app.state.executor = jobs.get_executer()

@app.on_event("shutdown")
async def on_shutdown():
   app.state.executor.shutdown()

@app.on_event("startup")
@repeat_every(seconds=60*60)  # 1 hour
def every_hour() -> None:
    logger.info('every_hour')
    jobs.expired_jobs_handler()
