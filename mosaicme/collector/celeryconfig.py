BROKER_URL = 'amqp://guest:guest@rabbit:5672//'
CELERY_RESULT_BACKEND = 'amqp://guest:guest@rabbit:5672//'

CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_ENABLE_UTC = True
