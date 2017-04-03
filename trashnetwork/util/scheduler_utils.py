import json

import pytz
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from trashnetwork import settings
from trashnetwork.util import mqtt_broker_utils


scheduler = None


def init_scheduler():
    global scheduler
    jobstores = {
        'default': RedisJobStore(db=settings.TN_SCHEDULER['REDIS_DB'])
    }
    executors = {
        'default': ThreadPoolExecutor(settings.TN_SCHEDULER['THREAD_POOL_SIZE']),
        'processpool': ProcessPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': settings.TN_SCHEDULER['MAX_JOB_INSTANCE']
    }
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
                                    timezone=pytz.timezone(settings.TIME_ZONE))
    scheduler.start()
    print('Scheduler is running...')


def stop_scheduler():
    global scheduler
    scheduler.shutdown(wait=False)
    print('Scheduler has stopped.')


def add_interval_job(job_id: str, job_func, minutes: int, args: list):
    scheduler.add_job(job_func, trigger='interval', minutes=int(minutes),
                      id=str(job_id), replace_existing=True, args=args)


JOB_CLEANING_REMINDER_PREFIX = 'cleaning_reminder/trash_'


def add_cleaning_reminder(trash_id: int):
    add_interval_job(job_id=JOB_CLEANING_REMINDER_PREFIX + str(trash_id),
                     job_func=job_cleaning_reminder,
                     minutes=settings.TN_CLEANING_REMINDER['INTERVAL_MINUTES'],
                     args=[trash_id])


def job_cleaning_reminder(trash_id: int):
    mqtt_broker_utils.publish_message(full_topic=settings.MQTT_TOPIC_CLEANING_REMINDER,
                                      message=json.dumps({'trash_id': int(trash_id)}),
                                      qos=0)

