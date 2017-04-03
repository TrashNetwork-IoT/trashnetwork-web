import signal
import sys
from django.apps import AppConfig
import django.dispatch
from trashnetwork.util import mqtt_broker_utils, scheduler_utils


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
        for t in models.Trash.objects.all():
            scheduler_utils.add_cleaning_reminder(t.trash_id)

        signal.signal(signal.SIGINT, self.on_server_shutdown)

    def on_server_shutdown(self, signal, frame):
        mqtt_broker_utils.disconnect_from_broker()
        scheduler_utils.stop_scheduler()
        self.shutdown_signal.send('system')
        sys.exit(0)
