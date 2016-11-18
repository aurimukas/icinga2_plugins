# -*- coding: UTF-8
"""
Celery service config.
"""
from celery import Celery
from argoss_libs.config import CELERY


class CeleryConfig:
    """
    Celery config object
    """
    result_expires = 600

# Creating Celery App
app = Celery('daemon',
             broker='redis://{0}:{1}/{2}'.format(CELERY['host'], CELERY['port'], CELERY['db']),
             backend='redis://{0}:{1}/{2}'.format(CELERY['host'], CELERY['port'], CELERY['db']),
             include=['celery_tasks'],
             )

# Applying Config object to Celery App
app.config_from_object(CeleryConfig)
