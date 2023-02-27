from .celery_app import celery_app 
from celery.utils.log import get_task_logger
from functools import partial
import boto3

import sys
sys.path.append('.')

from mosaic.mosaic import mosaic 

# Create the celery app and get the logger
logger = get_task_logger(__name__)

def task_update_progress(task, progress=None, task_id=None, total=100):    
    meta = {'progress': progress, 'total': total}
    task.update_state(task_id=task_id,state='PROGRESS', meta=meta )

import time

def now_ms():
    return int( time.time_ns() / (1000*1000) )

def since_ms( start_ms, finish_ms = None ):
    if finish_ms is None:
        finish_ms = now_ms()
    return finish_ms - start_ms

@celery_app.task(bind=True)
def mosaic_task(self,ops):

    uid = mosaic_task.request.id
    ops['uid'] = uid
    logger.info(f'ops : {ops}')
    
    progress_callback = partial(task_update_progress,task=self,task_id=uid)
    progress_callback(progress=0)

    start_ms = now_ms()
    rc, output_path = mosaic(ops,progress_callback)
    finish_ms = now_ms()
    duration_ms = since_ms(start_ms, finish_ms)

    progress_callback(progress=100)

    s3 = boto3.resource('s3')
    bucket = "mosaic-bucket"
    extra = {'ContentType': "image/jpeg"}

    s3.Bucket(bucket).upload_file(output_path, output_path, ExtraArgs=extra)
    location = boto3.client('s3').get_bucket_location(Bucket=bucket)['LocationConstraint']
    output_url = 'https://s3-' + location+'.amazonaws.com/'+bucket+'/' + output_path

    res = { 'rc':rc,
            'output_url': output_url,
            'start_ms'   : start_ms,
            'finish_ms'  : finish_ms,
            'duration_ms': duration_ms 
        }

    return res


