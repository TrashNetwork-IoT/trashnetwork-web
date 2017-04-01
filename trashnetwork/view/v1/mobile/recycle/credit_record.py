from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request

from trashnetwork.view.check_exception import CheckException
from trashnetwork.view.v1.mobile.recycle import account
from trashnetwork.view import result_code
from trashnetwork.util import view_utils, check_utils
from trashnetwork import models


@api_view(['GET'])
def get_credit_records(req: Request, start_time: str = None, end_time: str = None, limit_num: str = None):
    user = account.token_check(req)
    credit_record_list = []
    for cr in models.RecycleCreditRecord.objects.filter(
            view_utils.general_query_time_limit(end_time=end_time, start_time=start_time, user=user)):
        credit_record_list.append(view_utils.get_credit_record_dict(cr))
    if len(credit_record_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_CREDIT_RECORD_NOT_FOUND,
                             message=_('Credit record not found'))
    return view_utils.get_json_response(credit_record_list=credit_record_list)


@api_view(['POST'])
def recycle_bottle(req: Request):
    user = account.token_check(req)
    try:
        trash = models.Trash.objects.filter(trash_id=int(req.data['trash_id'])).get()
    except models.Trash.DoesNotExist:
        raise CheckException(result_code=result_code.MR_TRASH_NOT_FOUND,
                             message=_('Trash not found'))
    user_longitude = float(req.data['longitude'])
    user_latitude = float(req.data['latitude'])
    if not check_utils.check_location(longitude=user_longitude, latitude=user_latitude):
        raise CheckException(result_code=result_code.MR_ILLEGAL_LOCATION,
                             message=_('Illegal location'))
    if not check_utils.check_distance(p1_longitude=user_longitude, p1_latitude=user_latitude,
                                      p2_longitude=trash.longitude, p2_latitude=trash.latitude,
                                      distance_limit=50.0):
        raise CheckException(result_code=result_code.MR_TOO_FAR_AWAY_FROM_TRASH,
                             message=_('Too far away from specific trash'))
    quantity = int(req.data['quantity'])
    new_credit_record = models.RecycleCreditRecord(user=user,
                                                   good_description='Recycled bottle',
                                                   quantity=quantity,
                                                   credit=quantity)
    new_credit_record.save()
    user = models.RecycleAccount.objects.filter(user_id=user.user_id).get()
    user.credit += quantity
    user.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, message=_('Recycle bottle successfully'),
                                        credit=quantity)
