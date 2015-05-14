from __future__ import absolute_import, print_function
import argparse
import json
import logging
import logging.config
import os
import sys

import dotenv
import boto
from boto.s3.connection import S3Connection
import tweepy
from tweepy import OAuthHandler

from mosaicme.async.tasks import upload_image


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='MosaicMe Twitter History. Collects images from tweets containing the given hashtag. If a file called "max_id" is placed in the same directory, it will start processing tweets older than the ID contained in the file, otherwise it will start from the most recent tweet and create and update the "max_id" file.')
    parser.add_argument('-t', '--hashtag', help='Hashtag', required=True)
    parser.add_argument('-b', '--bucket', help='Bucket', required=True)
    parser.add_argument('-c', '--config',
                        help='Path to the Dotenv file. If not provided, it will try to get it from the base directory.',
                        required=False)
    args = parser.parse_args()

    if args.config:
        config_path = args.config
    else:
        config_path = os.path.join(BASE_DIR, '../../', '.env')

    if not os.path.exists(config_path):
        logger.error('Config file not found at {}'.format(config_path))
        sys.exit(2)

    logger.info('Reading dotenv file...')
    dotenv.read_dotenv(config_path)

    try:
        twitter_consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        twitter_consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
        twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

        s3_access_key = os.environ['S3_ACCESS_KEY']
        s3_secret_key = os.environ['S3_SECRET_KEY']
        s3_host = os.environ['S3_HOST']
        s3_port = int(os.environ['S3_PORT'])
        s3_is_secure = json.loads(os.environ['S3_HTTPS'].lower())

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
        s3_conn.get_bucket(args.bucket)
    except boto.exception.S3ResponseError:
        logger.error("Could not obtain bucket: %s", args.bucket)
        sys.exit(5)

    logger.info('Connection with object store verified successfully')

    s3_credentials = {'host': s3_host, 'port': s3_port, 'is_secure': s3_is_secure, 'access_key': s3_access_key,
                      'secret_key': s3_secret_key}

    if os.path.exists("max_id"):
        logger.info('Reading "max_id" file')
        with open("max_id", "r") as file_:
            max_id = int(file_.read().replace('\n', ''))
            logger.info('"max_id" set to "%d"', max_id)
    else:
        logger.info('"max_id" file not found. Not using the "max_id" parameter')
        max_id = None

    auth = OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)

    api = tweepy.API(auth)
    query = '#{}'.format(args.hashtag)

    while True:

        if max_id:
            with open('max_id', 'w') as file_:
                file_.write(str(max_id))

        tweets = api.search(q=query, count=100, max_id=max_id)

        if len(tweets) == 0:
            logger.info('No more tweets. Exiting...')
            sys.exit(0)

        for tweet in tweets:
            max_id = tweet.id
            data = tweet._json

            if 'entities' not in data:
                logger.debug('[Tweet %s] No media found', tweet.id_str)
                continue
            if 'media' not in data['entities']:
                logger.debug('[Tweet %s] No media found', tweet.id_str)
                continue
            if not data['entities']['media']:
                logger.debug('[Tweet %s] No media found', tweet.id_str)
                continue
            for media in data['entities']['media']:
                if media['type'] != 'photo':
                    continue
                media_url = media['media_url']
                media_id = media['id_str']
                logger.info('[Tweet %s] Media found. ID: %s - URL: %s', tweet.id_str, media_id, media_url)
                upload_image.delay(media_id, media_url, tweet.user.screen_name, args.bucket, s3_credentials, None)


if __name__ == "__main__":
    main()