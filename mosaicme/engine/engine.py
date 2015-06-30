__author__ = 'salemm4'
#!/usr/bin/env python
import pika
import time
import os.path
import shutil
import os
import configparser
import logging
import logging.config
import json;

def copySourceFile(imagename):

    logging.info("Read Source msg ...."+imagename)

    print "Copy Source File ...."
    # check if file exist under share/in
    src = "/mosaic/in/"+imagename
    dst = "/engine/tmp/"+imagename
    if(os.path.isfile(src)):
    # copy to destination process/tmp
        shutil.copyfile(src, dst)
        print " [x] Finished copying "+imagename+" locally"
        logging.info('[engine]  [x] Finished copying '+imagename+' locally')
        return True
    else:
        return False


def buildTiles():
    print "build Tiles ...."
    os.system("metapixel-prepare /mosaic/raw tiles/ --width=32 --height=32")
    print " [x] Finished building tiles"
    logging.info('[engine] [x] Finished building tiles')


def createMosaic(imagename):
    print "Create Mosaic ...."
    src = "/engine/tmp/"+imagename
    out = "/engine/tmp/mosaic-"+imagename
    dest="/engine/tiles/"
    os.system("metapixel --metapixel "+src+" "+out+" --library "+dest+" --scale=10 --distance=5")
    print " [x] Finished Creating Mosaic File"
    logging.info('[engine] [x] Finished Creating Mosaic File')


def createThumbnails(imagename):
    print "Create Thumbnails ...."
    global thm_size
    src = "/engine/tmp/mosaic-"+imagename
    out = "/engine/tmp/thm-"+imagename

    os.system("convert -thumbnail "+str(thm_size)+" "+src+" "+out)
    print " [x] Finished Creating Mosaic File"
    logging.info('[engine] [x] Finished Creating Mosaic File')

def moveFiles(imagename):
    print "Move Files...."
    src = "/engine/tmp/mosaic-"+imagename
    src2 = "/engine/tmp/thm-"+imagename
    dst = "/mosaic/out/large/"+imagename
    dst2 = "/mosaic/out/small/"+imagename
    if(os.path.isfile(src)):
        # copy to destination mosaic/out
            shutil.copyfile(src, dst)

    if(os.path.isfile(src2)):
        #  copy to destination mosaic/out
            shutil.copyfile(src2, dst2)

    print " [x] Finished moving files"
    logging.info('[engine] [x] Finished moving files')

def putMsg(msg):
    print "Put Msg ...."
    global hostname
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname))
    channel = connection.channel()
    channel.queue_declare(queue='mosaic-finish', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='mosaic-finish',
                          body=msg,
                          properties=pika.BasicProperties(
                             delivery_mode = 2, # make message persistent
                          ))
    print " [x] Sent %r" % (msg,)
    logging.info('[engine] [x] Sent %r' % (msg,))
    connection.close()

    print " [x] Finished Putting Msg"
    logging.info('[engine]  [x] Finished Putting Msg')


def callback(ch, method, properties, body):
    logging.info('[engine]  [x] Received %r' % (body,))
    print " [x] Received %r" % (body,)
    data=json.loads(body)
    image=data["media_id"]+".jpg"
    # copy file to local temp
    if(copySourceFile(image)):
    #covert share to small
        buildTiles()
        #call to create mosaic file
        createMosaic(image)
        #create thumnails
        createThumbnails(image)
        #move files
        moveFiles(image)
        #put msg
        putMsg(body)
    print " [x] Done"
    logging.info('[engine] Done')
    time.sleep(5)
    ch.basic_ack(delivery_tag = method.delivery_tag)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
logging.config.fileConfig(os.path.join(BASE_DIR, 'logging.conf'))
logger = logging.getLogger(__name__)

print "Read setting ini"
logger.info('[engine] Read Setting ini')
config = configparser.ConfigParser()
if(os.path.isfile('/mosaic/setting/engine.ini') ):
    config.read('/mosaic/setting/engine.ini')
else:
    config.read('engine.ini')

hostname =config['DEFAULT']['hostname']
thm_size =config['DEFAULT']['thm_size']
queueeng=config['DEFAULT']['queueeng']
queueout=config['DEFAULT']['queueout']

logging.info('[engine] Host '+hostname)
logging.info('[engine] Thum Size '+str(thm_size))
logging.info('[engine] Queue In '+queueeng)
logging.info('[engine] Queue Out '+queueout)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname))
channel = connection.channel()
channel.queue_declare(queue='mosaic-eng', durable=True)
print ' [*] Waiting for messages. To exit press CTRL+C'
logging.info('[engine]  [*] Waiting for messages. To exit press CTRL+C')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='mosaic-eng')

channel.start_consuming()

