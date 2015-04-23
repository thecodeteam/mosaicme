from django.conf.urls import patterns, url

urlpatterns = patterns(
    'mosaic.views',

    url(r'^$', 'index', name='index'),
)