import signal
import sys
from django.apps import AppConfig
import django.dispatch
from trashnetwork.util import mqtt_broker_utils


class TrashNetworkConfig(AppConfig):
    name = 'trashnetwork'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.shutdown_signal = django.dispatch.Signal()

    def ready(self):
        mqtt_broker_utils.init_client()
        mqtt_broker_utils.connect_to_broker()
        signal.signal(signal.SIGINT, self.on_server_shutdown)

    def on_server_shutdown(self, signal, frame):
        mqtt_broker_utils.disconnect_from_broker()
        self.shutdown_signal.send('system')
        sys.exit(0)
