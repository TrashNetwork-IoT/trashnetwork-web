from django.core.cache import cache
from django.db.models import Max
from django.views.generic.base import logger
from rest_framework.decorators import api_view
from rest_framework.request import Request

from trashnetwork import models
from trashnetwork.view.v1.mobile.recycle import account
from trashnetwork.util import view_utils
from trashnetwork import settings
import random
import datetime

CACHE_KEY_RED_PACKET_PREFIX = 'recycle_red_packet/'
JOB_RED_PACKET_POINT = 'red_packet_point'
RED_PACKET_PROBABILITY = 0


def clear_red_packet(max_point_id: int=None):
    if max_point_id is None:
        max_point_id = int(models.RecyclePoint.objects.all().aggregate(Max('point_id'))['point_id__max'])
    i = 1
    while i <= max_point_id:
        cache.delete('%s%d' % (CACHE_KEY_RED_PACKET_PREFIX, i))
        i += 1


def update_red_packet_point(args: dict):
    point_total = models.RecyclePoint.objects.all().count()
    max_point_id = int(models.RecyclePoint.objects.all().aggregate(Max('point_id'))['point_id__max'])
    clear_red_packet(max_point_id)

    red_packet_point_count = int(point_total * args['max_red_packet_point_ratio'])
    if red_packet_point_count < 1:
        red_packet_point_count = 1
    red_packet_point_count = random.randint(1, red_packet_point_count)

    i = 1
    while i <= red_packet_point_count:
        red_packet_point_id = random.randint(1, max_point_id)
        red_packet_total = random.randint(args['each_min_red_packet_credit'],
                                          args['each_max_red_packet_credit'])
        last_time = random.randint(args['each_min_last_time'],
                                   args['each_max_last_time'])
        cache.set('%s%d' % (CACHE_KEY_RED_PACKET_PREFIX, red_packet_point_id),
                  {'total': red_packet_total, 'expire': int(datetime.datetime.now().timestamp()) + last_time * 60},
                  None)
        i += 1
    global RED_PACKET_PROBABILITY
    RED_PACKET_PROBABILITY = args['probability']
    logger.info('Finish to refresh red packet point')


def check_red_packet_valid(red_packet: dict, recycle_point_id: int):
    if red_packet is None:
        return -1
    if datetime.datetime.now().timestamp() > red_packet['expire']:
        cache.delete('%s%d' % (CACHE_KEY_RED_PACKET_PREFIX, recycle_point_id))
        return -1
    if red_packet['total'] <= 0:
        cache.delete('%s%d' % (CACHE_KEY_RED_PACKET_PREFIX, recycle_point_id))
        return -1
    return red_packet['total']


@api_view(['GET'])
def get_all_recycle_points(req: Request):
    user = account.token_check(req=req, optional=True)
    if user is not None:
        user = models.RecycleAccount.objects.filter(user_id=user.user_id).get()
    result_list = []
    for rp in models.RecyclePoint.objects.all():
        if user is not None and user.account_type == models.RECYCLE_ACCOUNT_GARBAGE_COLLECTOR:
            rp_dict = view_utils.get_recycle_point_dict(point=rp, is_owner=True)
        else:
            rp_dict = view_utils.get_recycle_point_dict(point=rp, is_owner=False)
        red_packet = cache.get('%s%d' % (CACHE_KEY_RED_PACKET_PREFIX, rp.point_id))
        is_red_packet_point = check_red_packet_valid(red_packet, rp.point_id) > 0
        rp_dict.update(is_red_packet_point=is_red_packet_point)
        result_list.append(rp_dict)
    return view_utils.get_json_response(recycle_point_list=result_list)
