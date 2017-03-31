import base64
import datetime

from django.db.models import Q
from django.http import JsonResponse
from trashnetwork import models


def get_json_response(result_code: int = 0, message: str = '', status: int = 200, **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, status=status)


def get_cleaning_user_info_dict(user: models.CleaningAccount):
    portrait_base64 = base64.b64encode(user.portrait).decode()
    result = dict(name=user.name, gender=user.gender, account_type=user.account_type,
                  portrait=portrait_base64, user_id=user.user_id, phone_number=user.phone_number)
    return result


def get_recycle_user_basic_info_dict(user: models.RecycleAccount):
    result = dict(user_id=user.user_id, credit=user.credit)
    return result


def get_trash_info_dict(trash: models.Trash):
    return dict(trash_id=trash.trash_id, description=trash.description,
                longitude=trash.longitude, latitude=trash.latitude, bottle_recycle=trash.bottle_recycle)


def get_feedback_dict(feedback: models.Feedback):
    result = dict(title=feedback.title, text_content=feedback.text,
                  feedback_time=int(feedback.timestamp.timestamp()))
    if feedback.poster:
        result.update({'user_name': feedback.poster.user_name})
    return result


def general_query_time_limit(end_time=None, start_time=None, **kwargs):
    if end_time is not None:
        q = Q(timestamp__lte=datetime.datetime.fromtimestamp(int(end_time)))
    else:
        q = Q(timestamp__lte=datetime.datetime.now())
    if start_time is not None:
        q &= Q(timestamp__gte=datetime.datetime.fromtimestamp(int(start_time)))
    for k, v in kwargs.items():
        d = {k: v}
        q &= Q(**d)
    return q
