__author__ = 'salemm4'
#!/usr/bin/env python
import pika
import time
import os.path
import shutil
import os
import Image
import configparser

def copySourceFile(imagename):
    # check if file exist under share/in
    src = "/mosaic/in/"+imagename
    dst = "/engine/tmp/"+imagename
    if(os.path.isfile(src)):
    # copy to destination process/tmp
        shutil.copyfile(src, dst)
        print " [x] Finished copying % locally" %(imagename)
        return True
    else:
        return False


def buildTiles():
    os.system("metapixel-prepare /mosaic/raw tiles/ --width=32 --height=32")
    print " [x] Finished building tiles"


def createMosaic(imagename):
    src = "/engine/tmp/"+imagename
    out = "/engine/tmp/mosaic-"+imagename
    os.system("metapixel --metapixel "+src+" "+out+" --library destination --scale=10 --distance=5")
    print " [x] Finished Creating Mosaic File"


def createThumbnails(imagename):
    global thm_size
    src = "/engine/tmp/mosaic-"+imagename
    out = "/engine/tmp/thm_"+imagename
    Image.open(imagename).thumbnail((thm_size,thm_size)).save(out)
    print " [x] Finished Creating Mosaic File"


def moveFiles(imagename):
    src = "/engine/tmp/mosaic-"+imagename
    src2 = "/engine/tmp/thm-"+imagename
    dst = "/mosaic/out/large/mosaic-"+imagename
    dst2 = "/mosaic/out/small/thm-"+imagename
    if(os.path.isfile(src)):
        # copy to destination mosaic/out
            shutil.copyfile(src, dst)

    if(os.path.isfile(src2)):
        #  copy to destination mosaic/out
            shutil.copyfile(src2, dst2)

    print " [x] Finished moving files"


def putMsg(imagename):
    global hostname
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname))
    channel = connection.channel()
    channel.queue_declare(queue='mosaic-done', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='mosaic-done',
                          body=imagename,
                          properties=pika.BasicProperties(
                             delivery_mode = 2, # make message persistent
                          ))
    print " [x] Sent %r" % (imagename,)
    connection.close()

    print " [x] Finished Putting Msg"

config = configparser.ConfigParser()
config.read('engine.ini')
hostname =config['DEFAULT']['hostname']
thm_size =config['DEFAULT']['thm_size']
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname))
channel = connection.channel()
channel.queue_declare(queue='mosaic', durable=True)
print ' [*] Waiting for messages. To exit press CTRL+C'
def callback(ch, method, properties, body):
        print " [x] Received %r" % (body,)
        # copy file to local temp
        if(copySourceFile(body)):
            #covert share to small
            buildTiles()
            #call to create mosaic file
            createMosaic(body)
            #create thumnails
            createThumbnails(body)
            #move files
            moveFiles(body)
            #put msg
            putMsg(body)
        print " [x] Done"
        time.sleep(5)
        ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='mosaic')

channel.start_consuming()

