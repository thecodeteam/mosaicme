# Deployment guide

The easiest way to deploy MosaicMe is leveraging the Docker images we have created for each one of the components. In this guide we are going to go through the steps needed to deploy MosaicMe. We assume that you have a Docker environment ready.

We are going to use the following Docker images:

- [emccode/mosaicme-web](https://hub.docker.com/r/emccode/mosaicme-web/)
- [emccode/mosaicme-cacher](https://hub.docker.com/r/emccode/mosaicme-cacher/)
- [emccode/mosaicme-sync](https://hub.docker.com/r/emccode/mosaicme-sync/)
- [emccode/mosaicme-collector](https://hub.docker.com/r/emccode/mosaicme-collector/)
- [emccode/mosaicme-engine](https://hub.docker.com/r/emccode/mosaicme-engine/)

## Obtaining Twitter credentials

First of all we need to create a Twitter app and obtain the necessary tokens for MosaicMe to listen to a Twitter feed and post the resulting mosaics.

Go to https://apps.twitter.com/ and create an app for MosaicMe. Once created, go to the "Keys and Access Tokens" tab and generate an access token. You will need the following keys:

- Consumer Key (API Key)
- Consumer Secret (API Secret)
- Access Token
- Access Token Secret

## Configuring your object storage

MosaicMe stores uses an S3-compatible object storage to store source images and the final mosaics. The easiest way to try MosaicMe is using Amazon S3 service. You will need to create the following buckets for MosaicMe:

- `mosaic-in` for the mosaic requests from the Twitter feed
- `mosaic-raw` for the source images used to create the mosaics
- `mosaic-outlarge` for the resulting mosaics (high resolution)
- `mosaic-outsmall` for the resulting mosaics (low resolution, thumbnails)

You can also use EMC ECS Community Edition to easily create an object storage service: https://github.com/EMCECS/ECS-CommunityEdition

## RabbitMQ

MosaicMe uses RabbitMQ for communication between the different microservices. Let's run a RabbitMQ instance with Docker.

```
docker run -d --name rabbit -e RABBITMQ_NODENAME=my-rabbit rabbitmq
```

## Redis

MosaicMe uses Redis to cache metadata about the mosaics generated and stored in the object store.

```
docker run -d --name redis redis
```

## Engine

The engine component is the one in charge of generating the mosaics from a set of source images. It will read incoming mosaic requests from the `mosaic-eng` queue and post results to the `mosaic-finish` queue.

First of all let's create some directories in the host machine that will be shared with the engine container.

```bash
cd ~
mkdir -p mosaic/{setting,raw,in,out,logs}
mkdir -p mosaic/out/{large,small}
```

Now create a file named `engine.ini` in `mosaic/setting`

```
touch ~/mosaic/setting/engine.ini
```

and fill it with the following information:

```
[DEFAULT]
hostname=rabbit
thm_size=120
queueeng=mosaic-eng
queueout=mosaic-finish
```

Start the Docker container.

```
docker run -d --name mosaicme-engine -v ~/mosaic:/mosaic  -v ~/mosaic/logs:/var/log/mosaic emccode/mosaicme-engine
```

## Sync

> Note: the Sync service deployment is a little bit confusing and prone to errors, so we are in the process of updating it and will update this guide once the new version is released

This component will sync mosaic images between the engine and Object Storage backend.

Create a file named `ecsconfig.properties` in `mosaic/setting`.

```
touch ~/mosaic/setting/ecsconfig.properties
```

and fill it with the following content and replace the Twitter credentials with your own ones and the `proxy`, `username`, and `password` key with your S3 credentials.

```
objectType=S3
username=S3_ACCESS_KEY
password=S3_SECRET_ACCESS_KEY
proxy=http://S3_HOST:S3_PORT

s3collectbucket=mosaic-raw

emclocal=/mosaic/raw/
mosaicin=/mosaic/in/
mosaicoutlarge=/mosaic/large/
mosaicoutsmall=/mosaic/small/
inbucket=mosaic-in
outlargebucket=mosaic-outlarge
outsmallbucket=mosaic-outsmall
downloaderQueue=mosaic-in
engineQueue=mosaic-eng
uploaderQueue=mosaic-finish
twitterQueue=mosaic-done
queueHost=rabbit
twitterText=Hi @%s Here is your Mosaic:%s.More info at the ECS & EMC Code booths!
twitterhashtage=mosaicmetest
consumerKey=CONSUMER_KEY
consumerSecret=CONSUMER_SECRET
accessToken=ACCESS_TOKEN
accessTokenSecret=ACCESS_TOKEN_SECRET

mosaicweb=http://mosaicme.emccode.com/#/mosaic/
tweetlargeimage=0
bitlylogin=emccodemosaicme
bitlyapikey=R_ba21f62be4aa45c6bbb697ab6c137dd8
```

Run the download sync.

```
docker run -d --name mosaicme-sync-downloader -v ~/mosaic/logs:/var/log/mosaic -v ~/mosaic:/mosaic --link rabbit:rabbit emccode/mosaicme-sync /bin/startsyncdownload.sh
```

Run the upload sync.

```
docker run -d --name mosaicme-sync-uploader -v ~/mosaic/logs:/var/log/mosaic -v ~/mosaic:/mosaic --link rabbit:rabbit emccode/mosaicme-sync /bin/startsyncupload.sh
```

Run the raw images sync.

```
docker run -d --name mosaicme-sync-raw -v ~/mosaic/logs:/var/log/mosaic -v ~/mosaic:/mosaic --link rabbit:rabbit emccode/mosaicme-sync /bin/startsyncemc.sh
```

## Cacher

The cacher lists a S3 bucket and uses Redis to store information about all available mosaics.

Create a `.env` file in your working directory and fill it with the following information:

```
touch ~/.env
```

```
TWITTER_CONSUMER_KEY={{twitter_consumer_key}}
TWITTER_CONSUMER_SECRET={{twitter_consumer_secret}}
TWITTER_ACCESS_TOKEN={{twitter_access_token}}
TWITTER_ACCESS_TOKEN_SECRET={{twitter_access_token_secret}}
TWITTER_USERNAME={{twitter_username}}

S3_ACCESS_KEY=ACCESS_KEY
S3_SECRET_KEY=SECRET_KEY
S3_HOST=s3
S3_PORT=4569
S3_HTTPS=False

BUCKET_COLLECTOR=emcworld
BUCKET_IN=mosaic-in
BUCKET_OUT_LARGE=mosaic-outlarge
BUCKET_OUT_SMALL=mosaic-outsmall

RABBITMQ_HOST=rabbit
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

QUEUE_IN=mosaic-in
QUEUE_ENGINE=mosaic-eng
QUEUE_FINISH=mosaic-finish
QUEUE_DONE=mosaic-done
```

Launch the container.

```
docker run -d --name mosaicme-cacher --env-file .env --link redis:redis emccode/mosaicme-cacher
```

## Web UI

The web UI component will fetch mosaic information from Redis and display them in a user-friendly interface.

```
docker run -d --name mosaicme-web -p 0.0.0.0:8000:80 --env-file .env --link redis:redis emccode/mosaicme-web
```

Now you can open your browser and navigate to `http://localhost:8000`. You should see web UI but no mosaics yet.

## Collector

The collector is in charge of listening to a Twitter feed (hashtag), extracting the images from the tweets and uploading them to a selected bucket in the object storage backend.

First, let's kick off the worker that will do all the uploading and messaging work.

```
docker run -d --name mosaicme-collector-worker --link rabbit:rabbit -e C_FORCE_ROOT=1 emccode/mosaicme-collector celery -A tasks worker --loglevel=info
```

And now, let's run the MosaicMe collector with the selected queue, bucket, and hashtag. You can run as many collectors as you want with different configurations.

We are going to create two collectors: one to fill in the raw images bucket that will be used to build mosaics; and the other one to listen to mosaic request with a hashtag of our choice.

Raw images collector with a popular hashtag (#Cloud):

> Note that unlike the other collector, this one doesn't set the `MOSAIC_QUEUE` variable as we don't want to notify any other component about raw images.

```
docker run -d --name mosaicme-collector-raw --link rabbit:rabbit --env-file .env -e "MOSAIC_BUCKET=mosaic-raw" -e "MOSAIC_LISTEN_HASHTAG=Cloud" emccode/mosaicme-collector
```

Mosaic request collector with hashtag #mosaicme:

```
docker run -d --name mosaicme-collector-in --link rabbit:rabbit --env-file .env -e "MOSAIC_QUEUE=mosaic-in" -e "MOSAIC_BUCKET=mosaic-in" -e "MOSAIC_LISTEN_HASHTAG=mosaicme" emccode/mosaicme-collector
```

Give it some time to fill in the raw images bucket and then send a tweet containing an image and the hashtag #mosaicme and wait for your mosaic to generate and published to Twitter with the specified username.

You can now monitor the buckets and the logs from the different components to check how the whole system works together.
