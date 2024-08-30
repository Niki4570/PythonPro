from celery import Celery

app = Celery('myapp', broker='amqp://guest:guest@localhost:5672//', backend='rpc://')


app.conf.update(
    result_expires=3600,
)

app.autodiscover_tasks(['tasks'])
