# MosaicMe Uploader service

The MosaicMe application uses [Metapixel](https://www.complang.tuwien.ac.at/schani/metapixel/) to build the mosaics, but this program needs a database of raw images to build the mosaics.

The Engine service is a Golang application that receives a message from the Listener via RabbitMQ with tweet information, including an image URL. Like the following one:

```json
{
  "twitter_handler": "johndoe_NYC",
  "user_name": "John Doe",
  "img_url": "http://pbs.twimg.com/media/CrMjiYdW8AAHbhG.jpg"
}
```

This service contains the following routines:


-  Raw Images routine: It will download the raw images from S3 bucket for raw images. The name of the bucket will be passed as env. parameter.
-  Mosaic routine: It will listen to RabbitMQ to receive tweet information. It will download the image and store it locally. Then process it to create mosaic image using the raw images stores under the raw images folder.
-  Also The service has independent routine that download raw images from to a particular bucket in the object store with the objective of creating an image database and enable the Engine to build the mosaics.
-  Publish routine: It will upload the mosaic image to S3 bucket. The of the bucket will be pass as env parameter. Also the publish routine will tweet out the mosaic thumbnail out to user.   

[FLOW DIAGRAM]


## Usage

```
$ engine --help
Usage: engine  [-h/--help]
    -h, --help                       Prints this help
    -v, --version                    Prints the program version
```

The app expects the following environment variables, corresponding to the RabbitMQ and S3-compatible object store credentials.

* `RABBITMQ_HOST`
* `RABBITMQ_PORT`
* `RABBITMQ_USER`
* `RABBITMQ_PASSWORD`
* `S3_ACCESS_KEY`
* `S3_SECRET_KEY`
* `S3_HOST`
* `S3_PORT`
* `S3_REGION`
* `S3_BUCKET_RAW`
* `S3_BUCKET_MOSAIC` 
* `QUEUE_NAME`

## TODO

* Ability to configure HTTPS endpoint.
* Flow diagram

## Docker

You can build the production image with the provided `Dockerfile`.

```
docker build -t emccode/mosaicme-engine .
```

And run it.

```
docker run -d --env-file your.env emccode/mosaicme-engine
```

## Development

This service depends on two other backing service: RabbitMQ and a S3-compatible object store. The easiest way to simulate those services is running a Docker container.

First, start the RabbitMQ container.

```
docker run -d --name rabbit -p 5672:5672 rabbitmq
```

Then, we will use [`fake-s3`](https://github.com/jubos/fake-s3) as our S3 backend. It is an awesome tool that simulates the behavior of a real object store.

```
docker run -d --name s3 -p 4569:4569 lphoward/fake-s3
```

Now, install the dependencies.

```
bundle install
```

Export the following environment variables. You can also create a `.env` file and export it altogether.

```
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
S3_ACCESS_KEY=1234
S3_SECRET_KEY=1234
S3_HOST=localhost
S3_PORT=4569
S3_REGION=local
S3_BUCKET_RAW=mosaic-raw`
S3_BUCKET_MOSAIC=mosaic-out 
QUEUE_NAME=mosaic-queue
```

And now you can start working on the engine and run it with the following command

```
go run ./bin/engine
```
