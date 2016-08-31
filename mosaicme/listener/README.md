# MosaicMe Listener service

The MosaicMe Listener service is a Python application that connects to the Twitter Streaming API and listens for tweets containing one or many particular hashtags.

Once the application receives a tweet, it looks for an attached picture and obtains the URL. Then, it is going to send a message to the Engine service. The message is formatted in JSON like the following example.

```json
{
  "twitter_handler": "johndoe_NYC",
  "user_name": "John Doe",
  "img_url": "http://pbs.twimg.com/media/CrMjiYdW8AAHbhG.jpg"
}
```

The application is going to discard tweets that belong to the same user that is configured to publish tweets and those that do not contain an image.

![Flow chart](../../images/mosaicme-listener-flowchart.png)


## Usage

```
usage: listener.py [-h] [-t HASHTAG] [-q QUEUE]

MosaicMe Listener. Listens the Twitter feed of a selected hashtag, extracts
the tweeted images, and sends a notification to a RabbitMQ queue.

optional arguments:
  -h, --help            show this help message and exit
  -t HASHTAG, --hashtag HASHTAG
                        List of comma-separated hashtags. Do not include the #
                        sign. Overwritten by MOSAIC_LISTEN_HASHTAG environment
                        variable if present.
  -q QUEUE, --queue QUEUE
                        Queue name to send a message. Overwritten by
                        MOSAIC_QUEUE environment variable if present.
```

The app expects the following environment variables, corresponding to the Twitter and RabbitMQ credentials.

* `TWITTER_CONSUMER_KEY`
* `TWITTER_CONSUMER_SECRET`
* `TWITTER_ACCESS_TOKEN`
* `TWITTER_ACCESS_TOKEN_SECRET`
* `TWITTER_USERNAME`
* `RABBITMQ_HOST`
* `RABBITMQ_PORT`
* `RABBITMQ_USER`
* `RABBITMQ_PASSWORD`

Also, you can optionally provide the hashtag it listens to, and the queue to send messages to as environment variables.

* `MOSAIC_LISTEN_HASHTAG`
* `MOSAIC_QUEUE`


## Docker

You can build the production image with the provided `Dockerfile`.

```
docker build -t emccode/mosaicme-listener .
```

And run it.

```
docker run -d --env-file your.env emccode/mosaicme-listener -t mosaicme -q engine
```


## Development

For development purposes, you can launch a Docker container with RabbitMQ.

```
docker run -d --name rabbit rabbitmq
```

Build a Docker image for testing.

```
docker build -t listener .
```

And use the following command to run the component and your changes.

```
docker run -ti --rm --env-file your.env -v $(pwd):/usr/src/app --link rabbit:rabbit -e RABBITMQ_HOST=rabbit listener -t mosaicme -q engine
```

You don't need to rebuild the Docker image at every code change as the volume is mapped to the container.

You only need to rebuild the image when you add a new dependency.
