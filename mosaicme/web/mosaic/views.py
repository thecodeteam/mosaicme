import boto
import time
from boto.s3.connection import S3Connection
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View


def index(request):
    return render(request, 'index.html')


def mosaic_list(request):

    # data = dict()
    # data['images'] = []
    # data['images'].append({'id': '123', 'url': 'http://charleshood.net/wp-content/uploads/2010/05/IMG_2080.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://infocus.emc.com/wp-content/uploads/2013/06/8717630635_4d7c4bb014_z.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://jasonnash.files.wordpress.com/2012/05/lab-2.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://i.vimeocdn.com/video/437533496_640.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://oxygencloudblog.files.wordpress.com/2011/05/img_0016.jpg'})
    # data['images'].append({'id': '123', 'url': 'http://blogs.cisco.com/wp-content/uploads/935566_10151574064859817_836422499_n-550x365.jpg'})
    # data['images'].append({'id': '123', 'url': 'http://charleshood.net/wp-content/uploads/2010/05/IMG_2080.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://infocus.emc.com/wp-content/uploads/2013/06/8717630635_4d7c4bb014_z.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://jasonnash.files.wordpress.com/2012/05/lab-2.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://i.vimeocdn.com/video/437533496_640.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://oxygencloudblog.files.wordpress.com/2011/05/img_0016.jpg'})
    # data['images'].append({'id': '123', 'url': 'http://blogs.cisco.com/wp-content/uploads/935566_10151574064859817_836422499_n-550x365.jpg'})
    # data['images'].append({'id': '123', 'url': 'http://charleshood.net/wp-content/uploads/2010/05/IMG_2080.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://infocus.emc.com/wp-content/uploads/2013/06/8717630635_4d7c4bb014_z.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://jasonnash.files.wordpress.com/2012/05/lab-2.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://i.vimeocdn.com/video/437533496_640.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://oxygencloudblog.files.wordpress.com/2011/05/img_0016.jpg'})
    # data['images'].append({'id': '123', 'url': 'http://blogs.cisco.com/wp-content/uploads/935566_10151574064859817_836422499_n-550x365.jpg'})
    # data['images'].append({'id': '123', 'url': 'http://charleshood.net/wp-content/uploads/2010/05/IMG_2080.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://infocus.emc.com/wp-content/uploads/2013/06/8717630635_4d7c4bb014_z.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://jasonnash.files.wordpress.com/2012/05/lab-2.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://i.vimeocdn.com/video/437533496_640.jpg'})
    # data['images'].append({'id': '123', 'url': 'https://oxygencloudblog.files.wordpress.com/2011/05/img_0016.jpg'})
    # data['images'].append({'id': '123', 'url': 'http://blogs.cisco.com/wp-content/uploads/935566_10151574064859817_836422499_n-550x365.jpg'})
    #
    # data['size'] = len(data['images'])
    #
    # time.sleep(2)
    #
    # return JsonResponse(data)


    s3_conn = S3Connection(aws_access_key_id=settings.S3_ACCESS_KEY,
                           aws_secret_access_key=settings.S3_SECRET_KEY,
                           host=settings.S3_HOST,
                           port=settings.S3_PORT,
                           calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                           is_secure=settings.S3_HTTPS)
    try:
        bucket_small = s3_conn.get_bucket('mosaic-outsmall')
        bucket_large = s3_conn.get_bucket('mosaic-outlarge')
    except boto.exception.S3ResponseError, e:
        return JsonResponse({'error': 'Could not connect to object store'}, status=500)

    data = dict()
    data['mosaics'] = []

    for key in bucket_small:
        if key not in bucket_large:
            continue

        url_small = s3_conn.generate_url(1000*60*60*24*365, 'GET', bucket='mosaic-outsmall', key=key.name)
        url_large = s3_conn.generate_url(1000*60*60*24*365, 'GET', bucket='mosaic-outlarge', key=key.name)

        mosaic = dict()
        mosaic['id'] = key.name
        mosaic['url_small'] = 'https:' + url_small
        mosaic['url_large'] = 'https:' + url_large
        mosaic['username'] = 'Android'
        mosaic['date'] = datetime.datetime.now()

        data['mosaics'].append(mosaic)

    data['size'] = len(data['mosaics'])

    return JsonResponse(data)


def mosaic_detail(request, mosaic_id):

    s3_conn = S3Connection(aws_access_key_id=settings.S3_ACCESS_KEY,
                           aws_secret_access_key=settings.S3_SECRET_KEY,
                           host=settings.S3_HOST,
                           port=settings.S3_PORT,
                           calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                           is_secure=settings.S3_HTTPS)

    bucket_small = s3_conn.get_bucket('mosaic-outsmall', validate=False)
    bucket_large = s3_conn.get_bucket('mosaic-outlarge', validate=False)

    try:
        key_small = bucket_small.get_key(mosaic_id)
        key_large = bucket_large.get_key(mosaic_id)
    except boto.exception.S3ResponseError:
        return JsonResponse({'error': 'Could not obtain mosaic'}, status=500)

    url_small = s3_conn.generate_url(1000*60*60*24*365, 'GET', bucket='mosaic-outsmall', key=mosaic_id)
    url_large = s3_conn.generate_url(1000*60*60*24*365, 'GET', bucket='mosaic-outlarge', key=mosaic_id)

    mosaic = dict()
    mosaic['id'] = mosaic_id
    mosaic['url_small'] = 'https:' + url_small
    mosaic['url_large'] = 'https:' + url_large
    mosaic['username'] = 'Android'
    mosaic['date'] = key_large.last_modified

    return JsonResponse(mosaic)