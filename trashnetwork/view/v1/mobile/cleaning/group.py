from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from base64 import b64encode

from trashnetwork.models import *
from trashnetwork.util.view_utils import general_query_time_limit
from trashnetwork.view.check_exception import CheckException
from trashnetwork.view import result_code
from trashnetwork.util import view_utils


@api_view(['GET'])
def all_groups(req: Request):
    if not CleaningGroup.objects.all():
        raise CheckException(result_code=result_code.MC_GROUP_GROUP_NOT_FOUND,
                             status=status.HTTP_404_NOT_FOUND,
                             message=_('Group not found'))
    groups = []
    for group in CleaningGroup.objects.all():
        group_object = dict(group_id=group.group_id,
                            name=group.name,
                            portrait=b64encode(group.portrait),
                            member_list=[b.user.user_id for b in group.cleaninggroupmembership_set])
        groups.append(group_object)
    return view_utils.get_json_response(group_list=groups)


@api_view(['GET'])
def bulletin(req: Request, limit_num, **kwargs):
    bulletins = []
    for bulletin in CleaningBulletin.objects.filter(general_query_time_limit(**kwargs)).order_by('-timestamp')[:limit_num]:
        bulletin_object = dict(poster_id=bulletin.poster_id,
                               post_time=bulletin.timestamp.timestamp(),
                               title=bulletin.title,
                               text_content=bulletin.text)
        bulletins.append(bulletin_object)
    return view_utils.get_json_response(bulletin_list=bulletins)


@api_view(['POST'])
def new_bulletin(req: Request):
    pass

