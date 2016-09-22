import sys
import os
import json
import argparse
import logging
import logging.config
import signal
import tweepy
import urllib3
import requests
import requests.packages.urllib3

import pika
from retrying import retry

import requests


def main():
    try:
        rmq_host = os.getenv('RABBITMQ_HOST', 'rabbit')
        rmq_port = int(os.environ['RABBITMQ_PORT'])
        rmq_user = os.environ['RABBITMQ_USER']
        rmq_password = os.environ['RABBITMQ_PASSWORD']
        queue_name = os.environ['Queue_NAME']

        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=rmq_host, port=rmq_port, credentials=pika.PlainCredentials(rmq_user, rmq_password)))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name,durable=True))

            print(' [*] Waiting for Message. To exit press CTRL+C')

            def callback(ch, method, properties, body):
                print(" [x] %r" % body)
                tweet_back(body)
			ch.basic_ack(delivery_tag = method.delivery_tag)
            channel.basic_consume(callback, queue=queue_name)
            channel.start_consuming()

        except Exception as e:
            print('Could not connect to RabbitMQ. %s' % (e,))
            sys.exit(7)

        print('Connection with RabbitMQ verified successfully')

    except KeyError as e:
        print('Could not obtain environment variable: %s' % (e,))
        sys.exit(4)

    except Exception as e:
        print('Error: %s' % (e,))
        sys.exit(5)

    print('Twitter and RabbitMQ credentials loaded correctly from environment')


def tweet_back(message):
    try:
        twitter_consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        twitter_consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
        twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
        twitter_username = os.environ['TWITTER_USERNAME']
        tweet_msg =os.environ['TWEET_TEXT']
    except KeyError as e:
        print('Could not obtain environment variable: %s' % (e,))
        sys.exit(3)

    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)


    try:
        data = json.loads(message)
    except ValueError as e:
        print('Could not parse JSON data. %s' % (str(e),))
        return True


    twitter_handler = data['twitter_handler']
    url = data['img_url']

    tweetmsg = tweet_msg % twitter_handler

    requests.packages.urllib3.disable_warnings()
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_with_media(filename, status=tweetmsg)
        os.remove(filename)
    else:
        print("Unable to download image")

    print('complete')


if __name__ == "__main__":
    main()









