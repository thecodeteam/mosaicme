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
