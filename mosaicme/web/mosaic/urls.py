from django.conf.urls import patterns, url

urlpatterns = patterns(
    'mosaic.views',

    url(r'^mosaic/$', 'mosaic_list', name='mosaic_list'),
    url(r'^mosaic/(?P<mosaic_id>.*)/$', 'mosaic_detail', name='mosaic_detail'),

    url(r'^$', 'index', name='index'),


)