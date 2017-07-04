from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.utils.translation import ugettext as _

from trashnetwork import models
from trashnetwork.view import result_code
from trashnetwork.util import view_utils
from trashnetwork.view.check_exception import CheckException


@api_view(['GET'])
def get_events(req: Request, start_time: str = None, end_time: str = None, limit_num: str = None):
    event_list = []
    for e in models.Event.objects.filter(view_utils.general_query_time_limit(end_time=end_time, start_time=start_time))[:int(limit_num)]:
        event_list.append(view_utils.get_model_dict(e))
    if len(event_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_EVENT_NOT_FOUND, message=_('Event not found'))
    return view_utils.get_json_response(event_list=event_list)
