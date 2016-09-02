# MosaicMe Uploader service

The MosaicMe application uses [Metapixel](https://www.complang.tuwien.ac.at/schani/metapixel/) to build the mosaics, but this program needs a database of raw images to build the mosaics.

The Uploader service is a Ruby application that receives a message from the Listener via RabbitMQ with tweet information, including an image URL. Like the following one:

```json
{
  "twitter_handler": "johndoe_NYC",
  "user_name": "John Doe",
  "img_url": "http://pbs.twimg.com/media/CrMjiYdW8AAHbhG.jpg"
}
```

This service will obtain the image and uploads it to a particular bucket in the object store with the objective of creating an image database and enable the Engine to build the mosaics.

[FLOW DIAGRAM]


## Usage

```
$ ruby bin/uploader --help
Usage: uploader.rb -q QUEUE_NAME -b BUCKET_NAME [-h/--help]
    -q, --queue QUEUE_NAME           RabbitMQ queue name
    -b, --bucket BUCKET_NAME         Object store bucket where the image will be uploaded
    -h, --help                       Prints this help
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


## TODO

* Ability to configure HTTPS endpoint.
* Flow diagram
* Create Docker image
* Development instructions
