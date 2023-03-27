from celery.utils.log import get_task_logger
import boto3

# Create the celery app and get the logger
logger = get_task_logger(__name__)

def s3_upload(local_path, bucket_name, bucket_path, content_type = None ):

    s3 = boto3.resource('s3')
    extra = {'ContentType': content_type } if content_type else None
    
    error = False
    output_url = False

    try:
        s3.Bucket(bucket_name).upload_file(local_path, bucket_path, ExtraArgs=extra)
        location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        output_url = 'https://s3-' + location+'.amazonaws.com/'+bucket_name+'/' + bucket_path
        logger.info(f'local file :{local_path} uploaded to s3')

    except Exception as e:
        rc = type(e)
        error = str(e)

    res = { 
            'error'      : error,
            'output_url' : output_url
    }

    return res


