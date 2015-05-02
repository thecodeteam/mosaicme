from __future__ import absolute_import, print_function
import argparse
import json
import logging
import logging.config
import os
import dotenv
import sys
import boto
from boto.s3.connection import S3Connection
import redis
import time


WAIT_TIME = 30  # in seconds
CACHE_LIFE = 600  # in seconds

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='MosaicMe Cacher. Lists the buckets "mosaic-outlarge" and "mosaic-outsmall", generates a JSON object and stores it on the Redis cache to be consumed by the Web app.')
    parser.add_argument('-c', '--config',
                        help='Path to the Dotenv file. If not provided, it will try to get it from the base directory.',
                        required=False)
    args = parser.parse_args()

    if args.config:
        config_path = args.config
    else:
        config_path = os.path.join(BASE_DIR, '..', '.env')

    if not os.path.exists(config_path):
        logger.error('Config file not found at {}'.format(config_path))
        sys.exit(2)

    logger.info('Reading dotenv file...')
    dotenv.read_dotenv(config_path)

    try:
        s3_access_key = os.environ['S3_ACCESS_KEY']
        s3_secret_key = os.environ['S3_SECRET_KEY']
        s3_host = os.environ['S3_HOST']
        s3_port = int(os.environ['S3_PORT'])
        s3_is_secure = json.loads(os.environ['S3_HTTPS'].lower())

        redis_host = os.environ['REDIS_HOST']
        redis_port = int(os.environ['REDIS_PORT'])
        redis_db = int(os.environ['REDIS_DB'])

    except KeyError, e:
        logger.error('Could not obtain environment variable: %s', str(e))
        sys.exit(3)
    except Exception, e:
        logger.error('Error', e)
        sys.exit(4)

    logger.info('Dotenv variables loaded correctly')

    s3_conn = S3Connection(aws_access_key_id=s3_access_key,
                           aws_secret_access_key=s3_secret_key,
                           host=s3_host,
                           port=s3_port,
                           calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                           is_secure=s3_is_secure)

    logger.info('Checking connection with object store...')
    try:
        s3_conn.get_bucket("mosaic-outlarge")
    except boto.exception.S3ResponseError:
        logger.error("Could not obtain bucket: %s", args.bucket)
        sys.exit(5)

    logger.info('Connection with object store verified successfully')

    logger.info('Checking connection with Redis...')
    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    except redis.exceptions.ConnectionError:
        logger.error("Could not connect to redis.")
        sys.exit(6)
    logger.info('Connection with Redis verified successfully')

    while True:
        logger.info('Getting keys from object store...')

        try:
            bucket_small = s3_conn.get_bucket('mosaic-outsmall')
            bucket_large = s3_conn.get_bucket('mosaic-outlarge')
        except boto.exception.S3ResponseError, e:
            logger.error("Could not get bucket.")
            sys.exit(7)

        data = dict()
        data['mosaics'] = []

        for key in bucket_small:
            if key not in bucket_large:
                continue

            url_small = s3_conn.generate_url(1000*60*60*24*365, 'GET', bucket='mosaic-outsmall', key=key.name)
            url_large = s3_conn.generate_url(1000*60*60*24*365, 'GET', bucket='mosaic-outlarge', key=key.name)

            mosaic = dict()
            mosaic['id'] = key.name
            mosaic['url_small'] = 'https:' + url_small
            mosaic['url_large'] = 'https:' + url_large
            mosaic['username'] = 'EMCcorp'
            mosaic['date'] = key.last_modified
            r.set('mosaic:{}'.format(key.name), json.dumps(mosaic))
            data['mosaics'].append(mosaic)

        data['size'] = len(data['mosaics'])
        r.set('mosaic:all', json.dumps(data), ex=CACHE_LIFE)

        logger.info('Cached {} mosaics'.format(data['size']))
        logger.info('Sleeping for {} seconds'.format(WAIT_TIME))
        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()