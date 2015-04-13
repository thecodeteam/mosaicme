from __future__ import absolute_import

from celery import Celery

import boto
from boto.s3.connection import S3Connection

import logging
import logging.config
import os
import dotenv
import requests
import shutil
import json


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, '.imgtmp')
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger('twitterCollector')
dotenv.read_dotenv(os.path.join(BASE_DIR, '..', '.env'))

app = Celery('twitterCollector')
app.config_from_object('mosaicme.celeryconfig')

accessKeyId = os.environ['S3_ACCESS_KEY']
secretKey = os.environ['S3_SECRET_KEY']
host = os.environ['S3_HOST']
try:
    port = int(os.environ['S3_PORT'])
except:
    port = 80
try:
    is_secure = json.loads(os.environ['S3_HTTPS'].lower())
except:
    is_secure = False
bucket_collector = os.environ['BUCKET_COLLECTOR']
bucket_mosaic_in = os.environ['BUCKET_MOSAIC_IN']


@app.task
def upload_source_image(img_id, url):
    logger.debug('Downloading picture (ID: %s, URL: %s)', img_id, url)
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        logger.debug('Could not download picture (ID: %s, URL: %s)', img_id, url)
        return False

    pic_name = '{name}.{extension}'.format(name=img_id, extension='jpg')
    path = os.path.join(TMP_DIR, pic_name)
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    logger.debug('Picture downloaded successfuly into %s (ID: %s, URL: %s)', path, img_id, url)
    logger.debug('Uploading picture to object store (ID: %s)', img_id)
    conn = S3Connection(aws_access_key_id=accessKeyId,
                        aws_secret_access_key=secretKey,
                        host=host,
                        port=port,
                        calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                        is_secure=is_secure)
    try:
        bucket = conn.get_bucket(bucket_collector)
    except boto.exception.S3ResponseError:
        logger.error("Couldn't obtain bucket: %s", bucket_collector)
        return False

    key = bucket.get_key(pic_name, validate=False)
    try:
        key.set_contents_from_filename(path)
    except:
        logger.error("Couldn't upload file %s to bucket %s", path, bucket_collector)
        return False
    logger.info('Image uploaded successfully to object store (ID: %s)', img_id)

    try:
        os.remove(path)
        logger.debug('Removed temporary file at %s', path)
    except OSError:
        pass
    return True



@app.task
def upload_base_image(img_id, url):
    logger.debug('Downloading base image (ID: %s, URL: %s)', img_id, url)
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        logger.debug('Could not base picture (ID: %s, URL: %s)', img_id, url)
        return False

    pic_name = '{name}.{extension}'.format(name=img_id, extension='jpg')
    path = os.path.join(TMP_DIR, pic_name)
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    logger.debug('Picture downloaded successfuly into %s (ID: %s, URL: %s)', path, img_id, url)
    logger.debug('Uploading picture to object store (ID: %s)', img_id)
    conn = S3Connection(aws_access_key_id=accessKeyId,
                        aws_secret_access_key=secretKey,
                        host=host,
                        port=port,
                        calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                        is_secure=is_secure)
    try:
        bucket = conn.get_bucket(bucket_mosaic_in)
    except boto.exception.S3ResponseError:
        logger.error("Couldn't obtain bucket: %s", bucket_mosaic_in)
        return False

    key = bucket.get_key(pic_name, validate=False)
    try:
        key.set_contents_from_filename(path)
    except:
        logger.error("Couldn't upload file %s to bucket %s", path, bucket_mosaic_in)
        return False
    logger.info('Picture uploaded successfully to object store (ID: %s)', img_id)

    try:
        os.remove(path)
        logger.debug('Removed temporary file at %s', path)
    except OSError:
        pass
    return True
