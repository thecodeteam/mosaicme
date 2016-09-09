# MosaicMe Engine service

The Engine service uses [Metapixel](https://www.complang.tuwien.ac.at/schani/metapixel/) to build the mosaics, but this program needs a database of raw images to build the mosaics.

The Engine service is a Golang application that receives a message from the Listener via RabbitMQ with tweet information, including an image URL. Like the following one:

```json
{
  "twitter_handler": "johndoe_NYC",
  "user_name": "John Doe",
  "img_url": "http://pbs.twimg.com/media/CrMjiYdW8AAHbhG.jpg"
}
```

This service contains the following routines:


-  Raw images routine: It will download the raw images from S3 bucket for raw images. The name of the bucket will be passed as env. parameter.
-  Mosaic routine: It will listen to RabbitMQ to receive tweet information. It will download the image and store it locally. Then process it to create mosaic image using the raw images stores under the raw images folder.
-  Also The service has independent routine that download raw images from to a particular bucket in the object store with the objective of creating an image database and enable the Engine to build the mosaics.
-  Publish routine: It will upload the mosaic image to S3 bucket. The of the bucket will be pass as env parameter. Also the publish routine will tweet out the mosaic thumbnail out to user.   


![Engine Service Flow Chart](../../images/mosaicme-engine-flowchart.png)


## Usage

...

## Docker

...
