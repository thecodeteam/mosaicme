import boto
from boto.s3.connection import S3Connection
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View


def index(request):
    return render(request, 'index.html')


class MosaicView(View):
    def get(self, request):

        s3_conn = S3Connection(aws_access_key_id=settings.S3_ACCESS_KEY,
                               aws_secret_access_key=settings.S3_SECRET_KEY,
                               host=settings.S3_HOST,
                               port=settings.S3_PORT,
                               calling_format='boto.s3.connection.ProtocolIndependentOrdinaryCallingFormat',
                               is_secure=settings.S3_HTTPS)
        try:
            bucket = s3_conn.get_bucket('mosaic-outsmall')
        except boto.exception.S3ResponseError, e:
            return JsonResponse({'error': 'Could not connect to object store'}, status=500)

        data = dict()
        data['images'] = []

        for key in bucket:
            url = s3_conn.generate_url(1000*60*60*24*365, 'GET', bucket='mosaic-outsmall', key=key.name)
            data['images'].append({'url': 'http:' + url})

        data['size'] = len(data['images'])

        return JsonResponse(data)