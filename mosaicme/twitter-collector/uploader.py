from __future__ import absolute_import

from celery import Celery
import logging
import logging.config
import os
import requests
import shutil


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger('twitterCollector')

app = Celery('twitterCollector')
app.config_from_object('celeryconfig')


@app.task
def upload_picture(pic_id, url):
    logging.debug('Downloading picture (ID: %s, URL: %s', pic_id, url)
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        pic_name = '{name}.{extension}'.format(name=pic_id, extension='jpg')
        path = os.path.join(TMP_DIR, pic_name)
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        logging.debug('Picture downloaded successfuly into %s (ID: %s, URL: %s', path, pic_id, url)
        return True
    logging.debug('Could not download picture (ID: %s, URL: %s', pic_id, url)
    return False