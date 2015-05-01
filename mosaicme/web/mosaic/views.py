import time
import json

import boto
from boto.s3.connection import S3Connection
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from models import init_redis


def index(request):
    return render(request, 'index.html')


def mosaic_list(request):

    r = init_redis()
    mosaic_cache = r.get('mosaic:all')
    if mosaic_cache:
        return JsonResponse(json.loads(mosaic_cache))

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
        mosaic['username'] = 'EMCcorp'
        mosaic['date'] = key.last_modified

        r.set('mosaic:{}'.format(key.name), json.dumps(mosaic))

        data['mosaics'].append(mosaic)

    data['size'] = len(data['mosaics'])

    r.set('mosaic:all', json.dumps(data), ex=settings.CACHE_LIFE)

    return JsonResponse(data)


def mosaic_detail(request, mosaic_id):

    r = init_redis()
    mosaic_cache = r.get('mosaic:{}'.format(mosaic_id))
    if mosaic_cache:
        return JsonResponse(json.loads(mosaic_cache))

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
    mosaic['username'] = 'EMCcorp'
    mosaic['date'] = key_large.last_modified

    r.set('mosaic:{}'.format(mosaic_id), json.dumps(mosaic))

    return JsonResponse(mosaic)