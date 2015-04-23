from django.conf.urls import patterns, url
from mosaic.views import MosaicView

urlpatterns = patterns(
    'mosaic.views',

    url(r'^mosaic/$', MosaicView.as_view(), name='mosaic'),

    url(r'^$', 'index', name='index'),


)