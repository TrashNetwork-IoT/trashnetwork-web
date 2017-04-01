from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request

from trashnetwork.models import *
from trashnetwork.view.check_exception import CheckException
from trashnetwork.view import result_code
from trashnetwork.util import view_utils, check_utils
from trashnetwork.view.v1.mobile.cleaning import account


@api_view(['GET'])
def get_work_record(req: Request, limit_num: str, user_id: str = None, trash_id: str = None,
                    start_time: str = None, end_time: str = None):
    account.token_check(req)
    work_record_list = []
    q = CleaningWorkRecord.objects.filter(
        view_utils.general_query_time_limit(start_time=start_time, end_time=end_time))
    if user_id is not None:
        q.filter(user_id=int(user_id))
    if trash_id is not None:
        q.filter(trash_id=int(trash_id))
    for wr in q[:int(limit_num)]:
        work_record_list.append(view_utils.get_work_record(wr))
    if len(work_record_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MC_WORK_RECORD_NOT_FOUND,
                             message=_('Work record not found'))
    return view_utils.get_json_response(work_record_list=work_record_list)


@api_view(['POST'])
def post_work_record(req: Request):
    user = account.token_check(req=req, permission_limit=CLEANING_ACCOUNT_TYPE_CLEANER)
    try:
        trash = Trash.objects.filter(trash_id=int(req.data['trash_id'])).get()
    except Trash.DoesNotExist:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MC_TRASH_NOT_FOUND,
                             message=_('Trash not found'))
    user_longitude = float(req.data['longitude'])
    user_latitude = float(req.data['latitude'])
    if not check_utils.check_location(longitude=user_longitude, latitude=user_latitude):
        raise CheckException(result_code=result_code.MC_ILLEGAL_LOCATION,
                             message=_('Illegal location'))
    if not check_utils.check_distance(p1_longitude=user_longitude, p1_latitude=user_latitude,
                                      p2_longitude=trash.longitude, p2_latitude=trash.latitude,
                                      distance_limit=50.0):
        raise CheckException(result_code=result_code.MC_TOO_FAR_AWAY_FROM_TRASH,
                             message=_('Too far away from specific trash'))
    new_record = CleaningWorkRecord(user=user, trash=trash)
    new_record.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                        message=_('Post new work record successfully'))
