from django.utils.translation import ugettext as _
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from base64 import b64encode

from trashnetwork.models import *
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
def bulletin2(req: Request, group_id, limit_num):
    pass


@api_view(['GET'])
def bulletin3(req: Request, group_id, end_time, limit_num):
    pass


@api_view(['GET'])
def bulletin4(req: Request, group_id, start_time, end_time, limit_num):
    pass

def bulletin(req: Request, q: Q):
    pass

@api_view(['POST'])
def new_bulletin(req: Request):
    pass

