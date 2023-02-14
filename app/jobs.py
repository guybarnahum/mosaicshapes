# Async
import os
import asyncio
from concurrent.futures.process import ProcessPoolExecutor

# misc 
import logging
import traceback
import tempfile
import json

# app
from util import now_ms,since_ms
from typing import Dict
from uuid import uuid4

# runs
from run import run_defaults as JobCreateMosaic_fn

# get root logger
logger = logging.getLogger(__name__) # the __name__ resolve to "main" since we are at the root of the project. 
                                     # This will get the root logger since no logger in the configuration has this name.

def json_job_serializer(obj):
    '''JSON serializer for job objects not serializable by default json code'''

    if isinstance(obj, (Job, JobCreateMosaic)):
        return obj.toJSON()

    raise TypeError ("Type %s not serializable" % type(obj))

'''
'''
class Job: # (BaseModel):

    def __init__(self):
        self.uid = uuid4().hex
        self.name = 'base'
        self.fn = None
        self.args: Dict[str, str] = { 'uid': self.uid }
        
        self.result: int = None
        self.output: str = None

        self.start_ms: int  = -1
        self.finish_ms: int = -1
        self.delta_ms:  int = -1
        self.aborted: bool = False
        self.expired: bool = False

    def toJSON(self):
        js = json.dumps(self,default=lambda o: o.__dict__,sort_keys=False,indent=6)
        return js

    def delete(self):
        print(f'Job({name}) delete output {self.output}')

'''
'''
class JobCreateMosaic(Job):
   
    def __init__(self):
        
        super().__init__()
        
        self.name = 'createMosaic'
        self.fn = JobCreateMosaic_fn

        _,self.temp = tempfile.mkstemp(suffix = '.jpg') 
        self.args['temp'] = self.temp

    def delete(self):
        print(f'Job({name}) delete temp {self.temp}')
        super().delete()

'''
'''
class Jobs:

    jobs: Dict[str, Job] = {}
    executor: ProcessPoolExecutor = None
    
    def __init__(self):
        self.executor = ProcessPoolExecutor()

    def get_executer(self):
        return self.executor

    def add(self, job):
        self.jobs[job.uid] = job

    def get_job(self,uid):
        return self.jobs[uid]

    def all(self):
        return self.jobs

    def toJSON(self):
        jobs = self.jobs.values()
        last_job = next(reversed(jobs)) if jobs else None # O(1) - python 3.7 dict preserve order
        
        js = "{"
        for job in jobs:
            js = js + "\n\"" + job.uid + "\" : " + job.toJSON() 
            if job is not last_job:
                js = js + ","
            js = js + "\n"
        js = js + "}"
        return js

    '''
    '''
    async def run_job(self,job):

        loop = asyncio.get_event_loop()

        try:
            # wait and return result
            rc, output = await loop.run_in_executor(self.executor, job.fn, job.args)  
        except Exception as e:
            rc = str(e)
            tb = traceback.format_exc()
            msg = rc +' : '+ tb
            logger.error( msg )
            output = None

        return rc, output
    
    '''
    '''
    async def start_job(self, job) -> None:
        
        self.add(job)
        uid = job.uid
        job.args['uid'] = uid
        job.start_ms = now_ms()
        rc, output = await self.run_job(job)

        # job could have deleted...
        
        if uid in self.jobs:
            job = self.jobs[uid]
            job.delta_ms = since_ms(job.start_ms)
            job.finish_ms = now_ms()
            job.result = rc
            job.output = output
        else:
            logger.warn(f'job {uid} not found')

    '''
    '''
    def purge(self,uid):
        if uid in self.jobs:
            job = self.jobs[uid]
            if job.output is not None:
                os.remove(job.output)
            if job.temp is not None:
                os.remove(job.temp)
            del self.jobs[uid] 
            logger.info(f'purged job {uid}')
        else:
            logger.warn(f'purge job {uid} not found')

    '''
    '''
    def expired_jobs_handler(self):
        for uid in self.jobs:
            
            job = self.jobs[uid]

            if job.expired and since_ms(job.finish_ms) > 60 * 60 * 1000:
                self.purge(uid)
                continue

            # job running more than 5 min? If so, abort!
            if  job.finish_ms == -1 and since_ms(job.start_ms ) >  5 * 60 * 1000:
                job.finished = now_ms()
                job.aborted = True
                continue

            # job finished more than 30 min ago? If so, expire!
            if job.finish_ms != -1 and since_ms(job.finish_ms) > 30 * 60 * 1000:
                job.expired = True
                continue
