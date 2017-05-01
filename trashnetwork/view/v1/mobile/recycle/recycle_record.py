from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.utils.translation import ugettext as _

from trashnetwork import models
from trashnetwork.view.check_exception import CheckException
from trashnetwork.view.v1.mobile.recycle import account
from trashnetwork.util import view_utils
from trashnetwork.view import result_code


@api_view(['GET'])
def get_recycle_record(req: Request, start_time: str, end_time:str, limit_num: str):
    user = account.token_check(req=req, permission_limit=models.RECYCLE_ACCOUNT_GARBAGE_COLLECTOR)
    result_list = []
    for r in models.RecycleCleaningRecord.objects.filter(view_utils.general_query_time_limit(start_time=start_time,
                                                                                             end_time=end_time,
                                                                                             user=user))[:int(limit_num)]:
        result_list.append(view_utils.get_recycle_record_dict(r))
    if len(result_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_RECYCLE_RECORD_NOT_FOUND,
                             message=_('No record'))
    return view_utils.get_json_response(recycle_record_list=result_list)


@api_view(['POST'])
def post_recycle_record(req: Request):
    user = account.token_check(req=req, permission_limit=models.RECYCLE_ACCOUNT_GARBAGE_COLLECTOR)
    try:
        recycle_point = models.RecyclePoint.objects.filter(point_id=req.data['recycle_point_id']).get()
    except models.RecyclePoint.DoesNotExist:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_RECYCLE_RECORD_RECYCLE_POINT_NOT_FOUND,
                             message=_('Recycle point not found'))
    if recycle_point.owner_id != user.user_id:
        raise CheckException(result_code=result_code.MR_RECYCLE_POINT_NOT_MANAGED,
                             message=_('The recycle point does not be managed by you'))
    if recycle_point.bottle_num is not None and recycle_point.bottle_num == 0:
        raise CheckException(result_code=result_code.MR_RECYCLE_POINT_EMPTY,
                             message=_('The recycle point is empty'))
    new_record = models.RecycleCleaningRecord(user=user, recycle_point=recycle_point,
                                              bottle_num=recycle_point.bottle_num)
    new_record.save()
    if recycle_point.bottle_num is not None:
        recycle_point.bottle_num = 0
    recycle_point.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                        message=_('Post recycle record successfully'))
