from __future__ import absolute_import, print_function
import argparse

from boto.s3.connection import S3Connection
import boto
import pika
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from tasks import process_image

import json
import logging
import logging.config
import dotenv
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterListener(StreamListener):
    """
    This listener handles tweets that contain a particular hashtag and
    gets the pictures
    """

    def __init__(self, twitter_username, bucket, s3_credentials, rmq_credentials, queue=None):
        self.twitter_username = twitter_username
        self.bucket = bucket
        self.queue = queue
        self.s3_credentials = s3_credentials
        self.rmq_credentials = rmq_credentials

    def on_data(self, str_data):
        try:
            data = json.loads(str_data)
        except ValueError, e:
            logger.warning('[Tweet] Could not parse JSON data. %s', str(e))
            return True

        twitter_user = data['user']['screen_name']

        if twitter_user.lower() == self.twitter_username.lower():
            logger.info('[Tweet] Ignoring tweet by user "%s"' % (self.twitter_username, ))
            return True

        if 'extended_entities' not in data:
            logger.debug('[Tweet] No media found')
            return True
        if 'media' not in data['extended_entities']:
            logger.debug('[Tweet] No media found')
            return True
        if not data['extended_entities']['media']:
            logger.debug('[Tweet] No media found')
            return True
        for media in data['extended_entities']['media']:
            if media['type'] != 'photo':
                continue
            media_url = media['media_url']
            media_id = media['id_str']
            logger.info('[Tweet] Media found. ID: %s - URL: %s', media_id, media_url)
            process_image.delay(media_id, media_url, twitter_user, self.bucket, self.s3_credentials, self.rmq_credentials, queue=self.queue)
        return True

    def on_error(self, status):
        logger.error('Error from the Twitter feed: %s', status)


def main():
    parser = argparse.ArgumentParser(
        description='MosaicMe Twitter Collector. Listens on a hashtag and extracts the tweeted images.')
    parser.add_argument('-t', '--hashtag', help='List of comma-separated hashtags. Overwritten by MOSAIC_LISTEN_HASHTAG environment variable if present.', required=False)
    parser.add_argument('-b', '--bucket', help='Bucket.  Overwritten by MOSAIC_BUCKET environment variable if present', required=False)
    parser.add_argument('-q', '--queue',
                        help='Queue. If provided, it will send a message with the filename to the given queue. Overwritten by MOSAIC_QUEUE environment variable if present.',
                        required=False)
    parser.add_argument('-c', '--config',
                        help='Path to the Dotenv file to load environment variables.',
                        required=False)
    args = parser.parse_args()

    hashtags = os.getenv('MOSAIC_LISTEN_HASHTAG', args.hashtag)
    if not hashtags:
        logger.error('No hashtag provided.')
        sys.exit(1)
    hashtags = hashtags.split(",")
    hashtags = map(lambda x: '#'+x, hashtags)
    logger.info("Hashtags: %r" % (hashtags, ))

    bucket = os.getenv('MOSAIC_BUCKET', args.bucket)
    if not bucket:
        logger.error('No bucket provided.')
        sys.exit(2)
    logger.info("Bucket: %s" % (bucket, ))

    queue = os.getenv('MOSAIC_QUEUE', args.queue)
    if queue:
        logger.info("Queue: %s" % (queue, ))

    if args.config:
        config_path = args.config
        if not os.path.exists(config_path):
            logger.error('Config file not found at {}'.format(config_path))
            sys.exit(3)

        logger.info('Reading dotenv file...')
        dotenv.read_dotenv(config_path)

    try:
        twitter_consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        twitter_consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
        twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
        twitter_username = os.environ['TWITTER_USERNAME']

        s3_access_key = os.environ['S3_ACCESS_KEY']
        s3_secret_key = os.environ['S3_SECRET_KEY']
        s3_host = os.environ['S3_HOST']
        s3_port = int(os.environ['S3_PORT'])
        s3_is_secure = json.loads(os.environ['S3_HTTPS'].lower())

        rmq_host = os.getenv('RABBITMQ_HOST', 'rabbit')
        rmq_port = int(os.environ['RABBITMQ_PORT'])
        rmq_user = os.environ['RABBITMQ_USER']
        rmq_password = os.environ['RABBITMQ_PASSWORD']
    except KeyError, e:
        logger.error('Could not obtain environment variable: %s', str(e))
        sys.exit(4)
    except Exception, e:
        logger.error('Error: %s', str(e))
        sys.exit(5)

    logger.info('Env variables loaded correctly')

    s3_conn = S3Connection(aws_access_key_id=s3_access_key,
                           aws_secret_access_key=s3_secret_key,
                           host=s3_host,
                           port=s3_port,
                           calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                           is_secure=s3_is_secure)

    logger.info('Checking connection with object store (%s:%s)...' % (s3_host, s3_port))
    try:
        s3_conn.get_bucket(bucket)
    except Exception, e:
        logger.error("Could not obtain bucket: %s. %s" % (bucket, str(e)))
        sys.exit(6)

    logger.info('Connection with object store verified successfully')

    s3_credentials = {'host': s3_host, 'port': s3_port, 'is_secure': s3_is_secure, 'access_key': s3_access_key,
                      'secret_key': s3_secret_key}

    logger.info('Checking connection with RabbitMQ (%s:%s)...' % (rmq_host, rmq_port))
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=rmq_host, port=rmq_port, credentials=pika.PlainCredentials(rmq_user, rmq_password)))
        connection.close()
    except Exception, e:
        logger.error('Could not connect to RabbitMQ. %s', str(e))
        sys.exit(7)
    logger.info('Connection with RabbitMQ verified successfully')

    rmq_credentials = {'host': rmq_host, 'port': rmq_port, 'user': rmq_user,
                       'password': rmq_password}

    l = TwitterListener(twitter_username, bucket, s3_credentials, rmq_credentials, queue=queue)
    auth = OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)

    logger.info('Listening to hashtags {}'.format(hashtags))

    stream = Stream(auth, l)
    stream.filter(track=hashtags)


if __name__ == "__main__":
    main()
