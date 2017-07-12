from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request

from trashnetwork.view.check_exception import CheckException
from trashnetwork.view.v1.mobile.recycle import account, recycle_point
from trashnetwork.view import result_code
from trashnetwork.util import view_utils, check_utils
from trashnetwork import models, settings
import random


@api_view(['GET'])
def get_credit_records(req: Request, start_time: str = None, end_time: str = None, limit_num: str = None):
    user = account.token_check(req)
    credit_record_list = []
    for cr in models.RecycleCreditRecord.objects.filter(
            view_utils.general_query_time_limit(end_time=end_time, start_time=start_time, user=user))[:int(limit_num)]:
        credit_record_list.append(view_utils.get_model_dict(cr, excluded_fields=['user']))
    if len(credit_record_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_CREDIT_RECORD_NOT_FOUND,
                             message=_('Credit record not found'))
    return view_utils.get_json_response(credit_record_list=credit_record_list)


@api_view(['POST'])
def recycle_bottle(req: Request):
    user = account.token_check(req)
    try:
        rp = models.RecyclePoint.objects.filter(point_id=int(req.data['recycle_point_id'])).get()
    except models.RecyclePoint.DoesNotExist:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_CREDIT_RECORD_RECYCLE_POINT_NOT_FOUND,
                             message=_('Recycle point not found'))
    if rp.bottle_num is None:
        raise CheckException(result_code=result_code.MR_CREDIT_RECORD_RECYCLE_POINT_NOT_FOUND,
                             message=_('This recycle point does not accept bottles'))
    user_longitude = float(req.data['longitude'])
    user_latitude = float(req.data['latitude'])
    if not check_utils.check_location(longitude=user_longitude, latitude=user_latitude):
        raise CheckException(result_code=result_code.MR_ILLEGAL_LOCATION,
                             message=_('Illegal location'))
    if not check_utils.check_distance(p1_longitude=user_longitude, p1_latitude=user_latitude,
                                      p2_longitude=rp.longitude, p2_latitude=rp.latitude,
                                      distance_limit=50.0):
        raise CheckException(result_code=result_code.MR_TOO_FAR_AWAY_FROM_RECYCLE_POINT,
                             message=_('Too far away from specific recycle point'))
    quantity = int(req.data['quantity'])
    if quantity <= 0:
        quantity = 1
    elif quantity > settings.TN_RECYCLE_BOTTLE_MAX_QUANTITY:
        quantity = settings.TN_RECYCLE_BOTTLE_MAX_QUANTITY

    red_packet_credit = 0
    cache_red_packet = cache.get('%s%d' % (recycle_point.CACHE_KEY_RED_PACKET_PREFIX, rp.point_id))
    max_red_packet_credit = recycle_point.check_red_packet_valid(cache_red_packet, rp.point_id)
    if max_red_packet_credit > 0:
        if max_red_packet_credit > quantity:
            max_red_packet_credit = quantity
        if random.random() < recycle_point.RED_PACKET_PROBABILITY:
            red_packet_credit = random.randint(1, max_red_packet_credit)
            cache_red_packet['total'] -= red_packet_credit
            cache.set('%s%d' % (recycle_point.CACHE_KEY_RED_PACKET_PREFIX, rp.point_id), cache_red_packet, None)

    new_credit_record = models.RecycleCreditRecord(user=user,
                                                   item_description='Recycled bottle x%d' % quantity,
                                                   credit=quantity + red_packet_credit)
    new_credit_record.save()
    user = models.RecycleAccount.objects.filter(user_id=user.user_id).get()
    user.credit += new_credit_record.credit
    user.save()
    rp.bottle_num += quantity
    rp.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, message=_('Recycle bottle successfully'),
                                        credit=new_credit_record.credit, red_packet_credit=red_packet_credit)
