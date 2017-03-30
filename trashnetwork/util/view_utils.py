import base64
import datetime

from django.db.models import Q
from django.http import JsonResponse
from trashnetwork import models


def get_json_response(result_code: int = 0, message: str = '', status: int = 200, **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, status=status)


def get_datetime(unix_timestamp_ms: int = 0):
    if unix_timestamp_ms < 0:
        return None
    return datetime.datetime.fromtimestamp(unix_timestamp_ms / 1000)


def get_cleaning_user_info_dict(user: models.CleaningAccount):
    portrait_base64 = base64.b64encode(user.portrait).decode()
    result = dict(name=user.name, gender=user.gender, account_type=user.account_type,
                  portrait=portrait_base64, user_id=user.user_id, phone_number=user.phone_number)
    return result


def get_recycle_user_basic_info_dict(user: models.RecycleAccount):
    result = dict(user_id=user.user_id, credit=user.credit)
    return result


def general_time_limit(end_time: int =None, start_time: int =None, **kwargs):
    if not end_time:
        return Q(timestamp__lte=get_datetime())
    end_time = int(end_time)
    q = Q(timestamp__lte=datetime.datetime.fromtimestamp(end_time))
    if not start_time:
        return q
    q &= Q(timestamp__gte=datetime.datetime.fromtimestamp(start_time))
    for k, v in kwargs.items():
        if k.endswith('_id'):
            d = {k: v}
            q &= Q(**d)
    return q
