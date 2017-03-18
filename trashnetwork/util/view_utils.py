import base64
import datetime
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
