"""
Celery configuration for Event-Driven OCR processing
"""
from celery import Celery
import os
from kombu import Queue

def make_celery(app=None):
    """Create Celery instance for Flask app"""
    # Celery configuration
    celery_config = {
        'broker_url': os.getenv('REDIS_URL', 'redis://redis:6379/0'),
        'result_backend': os.getenv('REDIS_URL', 'redis://redis:6379/0'),
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'Asia/Ho_Chi_Minh',
        'enable_utc': True,
        'task_routes': {
            'tasks.ocr.process_ocr_task': {'queue': 'ocr_queue'},
            'tasks.ai.train_model_task': {'queue': 'ai_queue'},
            'tasks.notifications.send_notification': {'queue': 'notification_queue'},
        },
        'task_default_queue': 'default',
        'task_queues': (
            Queue('default'),
            Queue('ocr_queue'),
            Queue('ai_queue'),
            Queue('notification_queue'),
        ),
        # Task execution settings
        'worker_prefetch_multiplier': 1,
        'task_acks_late': True,
        'worker_disable_rate_limits': False,
        'task_compression': 'gzip',
        'result_compression': 'gzip',
        'result_expires': 3600,  # 1 hour
        
        # Retry settings
        'task_default_retry_delay': 60,  # 1 minute
        'task_max_retries': 3,
        
        # Monitoring
        'worker_send_task_events': True,
        'task_send_sent_event': True,
    }

    # Create Celery instance
    celery = Celery('invoice_backend')
    celery.conf.update(celery_config)

    if app:
        # Flask app context
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Create Celery instance for direct import
celery = make_celery()