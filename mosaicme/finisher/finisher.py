import logging
import logging.config
import os
import pika
import threading
import dotenv
import sys
import tweepy


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger('mosaicFinisher')
dotenv.read_dotenv(os.path.join(BASE_DIR, '..', '.env'))

try:
    consumer_key = os.environ['TWITTER_CONSUMER_KEY']
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
    access_token = os.environ['TWITTER_ACCESS_TOKEN']
    access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

    rmq_host = os.environ['RABBITMQ_HOST']
    rmq_port = int(os.environ['RABBITMQ_PORT'])
    rmq_user = os.environ['RABBITMQ_USER']
    rmq_password = os.environ['RABBITMQ_PASSWORD']
    listen_queue = os.environ['QUEUE_DONE']
except KeyError, e:
    logger.error('Could not obtain environment variable: %s', str(e))
    sys.exit(1)



# tweepy init
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# rabbitmq init
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=rmq_host, port=rmq_port, credentials=pika.PlainCredentials(rmq_user, rmq_password)))
channel = connection.channel()

channel.queue_declare(queue=listen_queue, durable=True)

print ' [*] Waiting for logs. To exit press CTRL+C'


def callback(ch, method, properties, body):
    # TODO: 1. check if the message complies with the protocol
    # TODO: 2. tweet out the mosaic with the URL
    print " [x] %r" % (body,)
    try:
        status = api.update_status(status=body)
        print status
        logger.info('Mosaic was tweeted out successfully!')
    except Exception as inst:
        logger.error('There was an error sending out the tweet: ', inst)


channel.basic_consume(callback,
                      queue=listen_queue,
                      no_ack=True)

channel.start_consuming()
