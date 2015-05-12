from __future__ import absolute_import
import json

import logging
import logging.config
import os
import shutil

from celery import Celery
import boto
from boto.s3.connection import S3Connection
import pika
import requests
import time
from retrying import retry


MAX_RETRIES = 3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, '.imgtmp')
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger(__name__)

app = Celery('twitterCollector')
app.config_from_object('mosaicme.celeryconfig')


@app.task
def process_image(img_id, url, twitter_user, bucket, s3_credentials, rmq_credentials, queue=None):

    logger.debug('Downloading picture (ID: %s, URL: %s)', img_id, url)
    try:
        img_name, path = download_file(url, img_id)
    except:
        logger.debug('Could not download picture (ID: %s, URL: %s)', img_id, url)
        return False
    logger.debug('Picture downloaded successfuly into %s (ID: %s, URL: %s)', path, img_id, url)

    logger.debug('Uploading picture to object store (ID: %s)', img_id)
    try:
        upload_object_to_bucket(s3_credentials, path, img_name, bucket)
    except:
        logger.error("Couldn't upload file %s to bucket %s.", path, bucket)
        return False
    logger.info('Image uploaded successfully to object store (ID: %s)', img_id)

    if queue:
        logger.info('Sending message to queue "%s" (ID: %s)', queue, img_id)
        try:
            message = {'twitter_user': twitter_user, 'media_id': img_id}
            send_message_to_queue(rmq_credentials, message, queue)
        except Exception, e:
            logger.error('Could not send message to RabbitMQ queue', e)
            False
        logger.info('Message sent to queue "%s" (ID: %s)', queue, img_id)

    try:
        os.remove(path)
        logger.debug('Removed temporary file at %s', path)
    except OSError:
        pass

    return True


@retry(wait_exponential_multiplier=10000, stop_max_attempt_number=3)
def download_file(url, image_id):
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception('Could not download picture (ID: %s, URL: %s)' % (image_id, url))

    img_name = '{name}.{extension}'.format(name=image_id, extension='jpg')
    path = os.path.join(TMP_DIR, img_name)
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    return img_name, path


@retry(wait_exponential_multiplier=10000, stop_max_attempt_number=3)
def upload_object_to_bucket(s3_credentials, path, object_name, bucket_name):
    conn = S3Connection(aws_access_key_id=s3_credentials['access_key'],
                        aws_secret_access_key=s3_credentials['secret_key'],
                        host=s3_credentials['host'],
                        port=s3_credentials['port'],
                        calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                        is_secure=s3_credentials['is_secure'])

    bucket = conn.get_bucket(bucket_name)
    key = bucket.get_key(object_name, validate=False)
    key.set_contents_from_filename(path)



@retry(wait_exponential_multiplier=10000, stop_max_attempt_number=3)
def send_message_to_queue(rmq_credentials, message, queue):

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rmq_credentials['host'], port=rmq_credentials['port'],
        credentials=pika.PlainCredentials(rmq_credentials['user'], rmq_credentials['password'])))

    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(exchange='',
                          routing_key=queue,
                          body=json.dumps(message),
                          properties=pika.BasicProperties(
                              delivery_mode=2,
                          ))
    connection.close()