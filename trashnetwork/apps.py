import signal
import sys
import datetime
from django.apps import AppConfig
import django.dispatch
from trashnetwork.util import mqtt_broker_utils, scheduler_utils
from trashnetwork import settings


class TrashNetworkConfig(AppConfig):
    name = 'trashnetwork'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.shutdown_signal = django.dispatch.Signal()

    def ready(self):
        mqtt_broker_utils.init_client()
        mqtt_broker_utils.connect_to_broker()
        scheduler_utils.init_scheduler()

        from trashnetwork import models
        from trashnetwork.view.v1.mobile.recycle import credit_rank, recycle_point
        for t in models.Trash.objects.all():
            scheduler_utils.add_cleaning_reminder(t.trash_id)
        scheduler_utils.add_interval_job(job_id='credit_rank/day', job_func=credit_rank.update_rank_list,
                                         minutes=settings.TN_RECYCLE_CREDIT_RANK['UPDATE_INTERVAL_MINUTES'],
                                         start_time=datetime.datetime.now() + datetime.timedelta(seconds=3),
                                         args=[credit_rank.RANK_LIST_TYPE_DAILY])
        scheduler_utils.add_interval_job(job_id='credit_rank/week', job_func=credit_rank.update_rank_list,
                                         minutes=settings.TN_RECYCLE_CREDIT_RANK['UPDATE_INTERVAL_MINUTES'],
                                         start_time=datetime.datetime.now() + datetime.timedelta(seconds=3),
                                         args=[credit_rank.RANK_LIST_TYPE_WEEKLY])
        signal.signal(signal.SIGINT, self.on_server_shutdown)

    def on_server_shutdown(self, signal, frame):
        mqtt_broker_utils.disconnect_from_broker()
        scheduler_utils.stop_scheduler()
        self.shutdown_signal.send('system')
        sys.exit(0)
