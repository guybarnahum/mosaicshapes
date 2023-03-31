import boto3
import logging
import json
import os
import tempfile
import urllib.request
import tempfile
import os
import imghdr
from shutil import copyfile
from mosaic import mosaic

s3 = boto3.resource("s3")

if logging.getLogger().hasHandlers():
    # The Lambda environment pre-configures a handler logging to stderr.
    # If a handler is already configured,`.basicConfig` does not execute.
    # Thus we set the level directly.
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    logger.info(f"Hello logging from {__name__}!")
    result = f"Success from {__name__}"

    logger.info("Event: %s" % json.dumps(event))

    bucket_info, object_info, error = lambda_parse_s3_event(event)

    if error:
        logger.error(error)
        return {"statusCode": 400, "body": error}
    else:
        logger.info(f"s3 event: bucket {bucket_info} object {object_info}")

    bucket = bucket_info["name"] if "name" in bucket_info else None
    key = object_info["key"] if "key" in object_info else None

    if key is None or not key.startswith("input/"):
        body = f"key {key} ignored ..."
        logger.info(body)
        return {"statusCode": 200, "body": body}

    args = {}
    args["uid"] = lambda_generate_uid(event)
    args["s3"] = {"bucket": bucket, "key": key}

    logger.info(f"args: {args}")

    lambda_generate_local_files(args)  # <-- needs cleanup(args)

    input_path = args["input_path"] if "input_path" in args else None
    output_path = args["output_path"] if "output_path" in args else None

    try:
        logger.info(">>>> start mosaic")
        mosaic(args)
        logger.info(">>>> finish mosaic")
        # copyfile(input_path, output_path)
    except Exception as e:
        error = str(e)
        logger.error(f"could not mosaic {input_path} to {output_path} due to {error}")
        lambda_cleanup_local_files(args)
        return {"statusCode": 400, "body": error}

    try:
        upload_local_to_s3(bucket=bucket, key=output_path, local_path=output_path)
    except Exception as e:
        error = str(e)
        logger.error(f"could not upload {output_path} to s3 due to {error}")

        lambda_cleanup_local_files(args)
        return {"statusCode": 400, "body": error}

    lambda_cleanup_local_files(args)
    return {"statusCode": 200, "body": result, "args": args}


def lambda_cleanup_local_files(args):
    logger.info(f"lambda_cleanup_local_files")
    if "cleanup-remove-files" in args:
        for file in args["cleanup-remove-files"]:
            logger.info(f"task_cleanup: remove {file}")
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    error = str(e)
                    logger.error(f"task_cleanup remove {file} exception {error}")
            else:
                logger.warning(f"file does not exists {file}")


def lambda_parse_s3_event(event):
    """
    Returns a tupple bucket, object, err
    """
    try:
        parsed = event["Records"][0]
    except Exception as e:
        err = str(e)
        return None, None, err

    if "s3" not in parsed:
        return None, None, "could not find s3 info in event"

    s3 = parsed["s3"]

    if "bucket" not in s3:
        logger.debug(f"s3 is {s3}")
        return None, None, "could not find s3 bucket info in event"

    bocket = s3["bucket"]  # { 'name':s3.bucket.name, 'arn': s3.bucket.arn }

    if "object" not in s3:
        logger.debug(f"s3 is {s3}")
        return bocket, None, "could not find s3 object info in event"

    object = s3["object"]  # { 'key':s3.object.key, 'size': s3.object.size }

    return bocket, object, None


def lambda_generate_uid(event=None):
    uid = 0
    try:
        uid = event["Records"][0]["responseElements"]["x-amz-request-id"]
    except Exception as e:
        logger.warn(str(e))
        import uuid  # make a UUID based on the host address and current time

        uid = uuid.uuid1()
    return uid


def lambda_generate_local_files(args):
    error = None

    # .............................................................. input_path
    #
    # Does not use random name, to avoid leaking files in case of lost worker
    # By using uid, a retried task would generate the same input_path ...
    #
    uid = args["uid"]
    input_path = args["input_path"] if "input_path" in args else get_temp_file(name=uid)

    if os.path.exists(input_path):
        os.remove(input_path)

    try:
        if "url" in args:
            url = args["url"]
            input_path = download_url(url, input_path)
            args["input_path"] = input_path
        elif "s3" in args:
            bucket = args["s3"]["bucket"]
            key = args["s3"]["key"]
            input_path = download_s3_to_local(bucket, key, input_path)
            args["input_path"] = input_path
        else:
            # process local image path
            logger.info(f"process local_path:{input_path}")

    except Exception as e:
        error = str(e)
        input_path = None

    logger.info(f"downloaded input_path: {input_path}")

    if input_path is not None:
        ext = imghdr.what(input_path)

        if ext == "jpeg":
            ext = "jpg"

        logger.info(f"input_path: {input_path} ext is {ext}")

        if ext:
            input_path_ext = input_path + "." + ext
            os.rename(input_path, input_path_ext)
            input_path = input_path_ext
            args["input_path"] = input_path

    if error:
        logger.error(f"Could not download : {error}")

    # ......................................................... output_path

    uid = args["uid"]
    output_path = "/tmp/output-" + uid + get_ext(input_path, with_dot=True)

    if "output_path" in args:
        output_path = args["output_path"]
    else:
        args["output_path"] = output_path

    # ............................................... invoke task with args

    args["cleanup-remove-files"] = [input_path, output_path]

    return error  # assignment


def get_ext(path, with_dot=False):
    basename = os.path.basename(path)  # os independent
    ext = ".".join(basename.split(".")[1:])  # <-- main part

    if ext is not None:
        ext = ext.lower()
        if with_dot:
            ext = "." + ext
    return ext


def get_temp_file(name=None, suffix=None):
    # _,tf = tempfile.mkstemp(suffix)
    if suffix is None:
        suffix = ""

    if name is None:
        name = os.urandom(8).hex() + suffix

    tf = os.path.join(tempfile.gettempdir(), name)
    return tf


def download_url(url, local_path, ua=True):
    logger.info(f"download_url url:{url} >> local path:{local_path}")

    if os.path.exists(local_path):
        logger.debug(f"local path exists ... using cached value")
        os.utime(local_path, None)
        return local_path

    try:
        if not ua or ua is False:
            logger.debug(f"User-Agent as urllib")
            urllib.urlretrieve(
                url, local_path
            )  # maybe blocked by some servers due to user-agent
        else:
            ua = (
                ua
                if isinstance(ua, str)
                else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
            )
            logger.debug(f"User-Agent as {ua}")

            headers = {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
                "Accept-Encoding": "none",
                "Accept-Language": "en-US,en;q=0.8",
                "Connection": "keep-alive",
            }

            request_ = urllib.request.Request(
                url, None, headers
            )  # The assembled request
            response = urllib.request.urlopen(request_)  # store the response

            # create a new file and write the image
            f = open(local_path, "wb")
            f.write(response.read())
            f.close()

    except Exception as e:
        logger.error(str(e))

    return local_path


def download_s3_to_local(bucket=None, key=None, local_path=None):
    try:
        s3.meta.client.download_file(bucket, key, local_path)
    except Exception as e:
        error = str(e)
        logger.error(error)
        local_path = None
    return local_path


def upload_local_to_s3(bucket=None, key=None, local_path=None):
    key = key.replace("/tmp/", "output/")
    extra_args = {"ContentType": "image/jpeg", "ACL": "public-read"}
    logger.info(f"upload {local_path} to {bucket}:{key}")
    s3.Bucket(bucket).upload_file(local_path, key, ExtraArgs=extra_args)
