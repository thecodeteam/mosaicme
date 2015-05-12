To start the async tasks you just need to run the following command from the project root directory.

    $ celery -A mosaicme.twitter-collector.tasks worker --loglevel=info

This will tell Celery where the tasks are located and it will create a worker to start listening to job requests.
