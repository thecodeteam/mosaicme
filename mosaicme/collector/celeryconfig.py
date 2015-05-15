BROKER_URL = 'amqp://guest:guest@rabbit:5672//'
CELERY_RESULT_BACKEND = 'amqp://guest:guest@rabbit:5672//'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_ENABLE_UTC = True
