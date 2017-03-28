import threading
import time
import queue

from trashnetwork import settings
import paho.mqtt.client as mqtt_client

TOPIC_TYPE_PUBLIC = 0
TOPIC_TYPE_PRIVATE = 1
TOPIC_TYPE_GROUP = 2

USER_DATA_FIRST_CONNECT = 'first_connect'
MQTT_ACTION_SUBSCRIPTION = 'subscription'
MQTT_ACTION_PUBLISH = 'publish'
KEY_MQTT_ACTION = 'mqtt_action'
KEY_MQTT_PAYLOAD = 'mqtt_payload'
KEY_MQTT_QOS = 'mqtt_qos'
KEY_MQTT_TOPIC = 'mqtt_topic'
KEY_MQTT_RETAIN = 'mqtt_retain'

broker_client = None
mqtt_queue = None


def mqtt_subscribe(topic: str, qos: int):
    global broker_client
    result, mid = broker_client.subscribe(topic=topic, qos=qos)
    if result == mqtt_client.MQTT_ERR_SUCCESS:
        print('Subscribe topic <' + topic + '> successfully.')
        return True
    return False


def mqtt_publish(topic: str, payload: str, qos: int, retain: bool):
    global broker_client
    result, mid = broker_client.publish(topic=topic, payload=payload, qos=qos, retain=retain)
    if result == mqtt_client.MQTT_ERR_SUCCESS:
        print('Publish message on topic <' + topic + '> successfully.')
        return True
    return False


def broker_loop():
    global broker_client
    global mqtt_queue
    mqtt_queue = queue.Queue()
    while broker_client is not None:
        try:
            mqtt_action = mqtt_queue.get(block=True, timeout=3)
            while broker_client is not None:
                if mqtt_action[KEY_MQTT_ACTION] == MQTT_ACTION_SUBSCRIPTION:
                    if mqtt_subscribe(topic=mqtt_action[KEY_MQTT_TOPIC], qos=mqtt_action[KEY_MQTT_QOS]):
                        break
                    time.sleep(1)
                if mqtt_action[KEY_MQTT_ACTION] == MQTT_ACTION_PUBLISH:
                    if mqtt_publish(topic=mqtt_action[KEY_MQTT_TOPIC], qos=mqtt_action[KEY_MQTT_QOS],
                                    payload=mqtt_action[KEY_MQTT_PAYLOAD], retain=mqtt_action[KEY_MQTT_RETAIN]):
                        break
                    time.sleep(1)
                else:
                    break
        except queue.Empty:
            continue
    mqtt_queue = None


def on_broker_connect(client: mqtt_client.Client, userdata: dict, flags, rc):
    print('Connected with MQTT broker with result code ' + str(rc))
    if userdata[USER_DATA_FIRST_CONNECT]:
        if int(rc) != 0:
            raise Exception('Failed to connect to MQTT broker.')
        client.user_data_set({USER_DATA_FIRST_CONNECT: False})


def init_client():
    global broker_client
    broker_client = mqtt_client.Client(client_id=settings.TN_MQTT_BROKER['CLIENT_ID'], clean_session=False)
    broker_client.user_data_set({USER_DATA_FIRST_CONNECT: True})
    broker_client.username_pw_set(username=settings.TN_MQTT_BROKER['USERNAME'],
                                  password=settings.TN_MQTT_BROKER['PASSWORD'])
    broker_client.on_connect = on_broker_connect


def connect_to_broker():
    global broker_client
    broker_client.connect(host=settings.TN_MQTT_BROKER['HOST'], port=int(settings.TN_MQTT_BROKER['PORT']),
                          keepalive=15)
    broker_client.loop_start()
    t = threading.Thread(target=broker_loop)
    t.setDaemon(True)
    t.start()


def disconnect_from_broker():
    global broker_client
    if broker_client is None:
        return
    broker_client.disconnect()
    print('Disconnected from MQTT broker.')
    broker_client = None


def subscribe_topic(full_topic: str, qos: int = 1, max_retry: int = 5):
    """
    :type topic_user: micronurse_webserver.models.Account
    """
    global broker_client
    global mqtt_queue
    if broker_client is None or mqtt_queue is None:
        return
    mqtt_queue.put(
        item={KEY_MQTT_ACTION: MQTT_ACTION_SUBSCRIPTION, KEY_MQTT_TOPIC: full_topic, KEY_MQTT_QOS: qos},
        block=True,
        timeout=3
    )


def add_message_callback(topic_filter: str, callback):
    global broker_client
    if broker_client is None:
        return
    broker_client.message_callback_add(sub=topic_filter, callback=callback)


def publish_message(full_topic: str, message: str, topic_user = None, qos: int = 0, retain: bool = False):
    """
    :type topic_user: micronurse_webserver.models.Account
    """
    global broker_client
    global mqtt_queue
    if broker_client is None or mqtt_queue is None:
        return
    mqtt_queue.put(
        item={KEY_MQTT_ACTION: MQTT_ACTION_PUBLISH, KEY_MQTT_TOPIC: full_topic,
              KEY_MQTT_PAYLOAD: message, KEY_MQTT_QOS: qos, KEY_MQTT_RETAIN: retain},
        block=True,
        timeout=3
    )


def get_full_topic(topic: str, topic_type: int, owner_id: int = None):
    full_topic = topic + '/' + str(topic_type)
    if owner_id is not None:
        full_topic += '/' + str(owner_id)
    return full_topic

