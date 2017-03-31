from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.utils.translation import ugettext as _

from trashnetwork import models
from trashnetwork.view import result_code
from trashnetwork.util import view_utils
from trashnetwork.view.check_exception import CheckException


@api_view(['GET'])
def all_trashes(req: Request):
    trash_list = []
    for t in models.Trash.objects.all():
        trash_list.append(view_utils.get_trash_info_dict(t))
    return view_utils.get_json_response(trash_list=trash_list)


@api_view(['GET'])
def get_feedback(req: Request, limit_num: str, start_time: str = None, end_time: str = None):
    feedback_list = []
    for fb in models.Feedback.objects.filter(
            view_utils.general_query_time_limit(end_time=end_time, start_time=start_time))[:int(limit_num)]:
        feedback_list.append(view_utils.get_feedback_dict(fb))
    if len(feedback_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MP_FEEDBACK_NOT_FOUND,
                             message=_('No feedback'))
    return view_utils.get_json_response(feedback_list=feedback_list)
