import boto
from boto.s3.connection import S3Connection
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View


def index(request):
    #
    # images = []
    # images.append('http://charleshood.net/wp-content/uploads/2010/05/IMG_2080.jpg')
    # images.append('https://infocus.emc.com/wp-content/uploads/2013/06/8717630635_4d7c4bb014_z.jpg')
    # images.append('https://jasonnash.files.wordpress.com/2012/05/lab-2.jpg')
    # images.append('https://i.vimeocdn.com/video/437533496_640.jpg')
    # images.append('https://oxygencloudblog.files.wordpress.com/2011/05/img_0016.jpg')
    # images.append('http://blogs.cisco.com/wp-content/uploads/935566_10151574064859817_836422499_n-550x365.jpg')
    #
    # data = dict()
    # data['images'] = images

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
            bucket = s3_conn.get_bucket('mosaic-outlarge')
        except boto.exception.S3ResponseError, e:
            return JsonResponse({'error': 'Could not connect to object store'}, status=500)

        data = dict()
        data['images'] = []

        for key in bucket:
            data['images'].append(key.name)

        data['size'] = len(data['images'])

        return JsonResponse(data)