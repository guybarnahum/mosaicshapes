from celery import Task as celeryTask
from celery_app import celery_app 
from celery.utils.log import get_task_logger
from functools import partial

import os
import worker.aws as aws
import worker.worker_util as worker_util

# try without this vv
import sys
sys.path.append('.')

from mosaic.mosaic import mosaic 

# Create the celery app and get the logger
logger = get_task_logger(__name__)

# configure celecry_app to retiry lost workers
celery_app.conf.task_reject_on_worker_lost = True 
celery_app.conf.task_acks_late = True

class celeryTaskWithRetry(celeryTask):
    autoretry_for = (Exception, KeyError)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True

def task_cleanup(args):
    logger.info(f'task_cleanup')
    if 'cleanup-remove-files' in args:
        for file in args['cleanup-remove-files']:
            logger.info(f'task_cleanup: remove {file}')
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    error = str(e)
                    logger.error(f'task_cleanup remove {file} exception {error}')
            else:
                logger.warning(f'file does not exists {file}')

def task_update_progress(task, progress=None, task_id=None, total=100):    
    meta = {'progress': progress, 'total': total}
    task.update_state(task_id=task_id,state='PROGRESS', meta=meta )

def task_wrapper(task, fn, args):
    
    uid = task.request.id
    args['uid'] = uid
    logger.info(f'celery_app.task_warpper : {args}')

    progress_callback = partial(task_update_progress,task=task,task_id=uid)
    progress_callback(progress=0)

    # call actual task logic
    start_ms = worker_util.now_ms()
    error = None

    logger.info(f"calling task...")

    try:
        output_path = fn(args,progress_callback)
    except Exception as e:
        output_path = None
        error = str(e)
    
    logger.info(f"returning from task... error:{error}, output_path:{output_path}")

    finish_ms   = worker_util.now_ms()
    duration_ms = worker_util.since_ms(start_ms, finish_ms)

    progress_callback(progress=100)
    
    if output_path:
       # export result
        # todo: make it a task with retries logic
        res = aws.s3_upload(output_path, 'mosaic-bucket', output_path, content_type = 'image/jpeg')
    else:
        res = build_result(error)

    task_cleanup(args)
    
    res['start_ms'   ] = start_ms
    res['finish_ms'  ] = finish_ms
    res['duration_ms'] = duration_ms

    return res

def build_result(output_url=None, error=None):
    res = {}
    if output_url:
        res['output_url'] = output_url
    if error:
        res['error'] = error
    return res

@celery_app.task(bind=True,base=celeryTaskWithRetry)
def mosaic_task(self,args):

    args['uid'] = self.request.id

    error = worker_util.generate_local_input_output_files(args)
    if error:
        res = build_result(error=error)
        return res

    res = task_wrapper(self, mosaic, args)
    return res


