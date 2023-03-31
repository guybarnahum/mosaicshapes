import json
import logging

import boto3

if logging.getLogger().hasHandlers():
    # The Lambda environment pre-configures a handler logging to stderr.
    # If a handler is already configured,`.basicConfig` does not execute.
    # Thus we set the level directly.
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    logger.info("Hello logging from LambdaTest!")
    result = f"Success from {__name__}"

    logger.info("Event: %s" % json.dumps(event))

    return {"statusCode": 200, "body": result}
