import logging
import logging.config
import os
import redis
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
except KeyError, e:
    logger.error('Could not obtain environment variable: %s', str(e))
    sys.exit(1)


class Listener(threading.Thread):

    def __init__(self, r, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
        # tweepy init
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def work(self, item):
        # TODO: 1. check if the message complies with the protocol
        # TODO: 2. get the mosaic URI
        # TODO: 3. upload the mosaic to the object store and get the public URL (large and small)
        # TODO: 4. tweet out the mosaic with the URL

        # ignore subscribe messages
        if item['type'] == 'subscribe':
            return

        print item['channel'], ":", item['data']
        try:
            status = self.api.update_status(status=item['data'])
            print status
            logger.info('Mosaic was tweeted out successfully!')
        except Exception as inst:
            logger.error('There was an error sending out the tweet: ', inst)

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                self.work(item)


if __name__ == "__main__":
    client = Listener(redis.Redis(), ['mosaic-finish'])
    client.start()