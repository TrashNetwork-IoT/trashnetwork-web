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
def all_groups(req: Request):
    user = account.token_check(req)
    groups = []
    try:
        groups.append(view_utils.get_group_dict(CleaningGroup.objects.filter(group_id=SPECIAL_WORK_GROUP_ID).get()))
    except CleaningGroup.DoesNotExist:
        pass
    for gm in CleaningGroupMembership.objects.filter(user=user):
        groups.append(view_utils.get_group_dict(gm.group))
    if len(groups) == 0:
        raise CheckException(result_code=result_code.MC_GROUP_NOT_FOUND,
                             status=status.HTTP_404_NOT_FOUND,
                             message=_('Group not found'))
    return view_utils.get_json_response(group_list=groups)


@api_view(['GET'])
def bulletin(req: Request, group_id: str, limit_num: str, start_time: str = None, end_time: str = None):
    user = account.token_check(req)
    if not check_utils.check_group_member(user_id=user.user_id, group_id=int(group_id)):
        raise CheckException(result_code=result_code.MC_USER_NOT_GROUP_MEMBER,
                             message=_('User does not belong to this group'))
    bulletins = []
    for b in CleaningGroupBulletin.objects.filter(
            view_utils.general_query_time_limit(start_time=start_time, end_time=end_time, group_id=int(group_id)))[:int(limit_num)]:
        bulletins.append(view_utils.get_bulletin_dict(b))
    if len(bulletins) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MC_GROUP_BULLETIN_NOT_FOUND,
                             message=_('Bulletin not found'))
    return view_utils.get_json_response(bulletin_list=bulletins)


@api_view(['POST'])
def post_bulletin(req: Request):
    user = account.token_check(req=req, permission_limit=CLEANING_ACCOUNT_TYPE_MANAGER)
    if not check_utils.check_group_member(user_id=user.user_id, group_id=int(req.data['group_id'])):
        raise CheckException(result_code=result_code.MC_USER_NOT_GROUP_MEMBER,
                             message=_('User does not belong to this group'))
    new_bulletin = CleaningGroupBulletin(group_id=int(req.data['group_id']),
                                         poster=user, title=str(req.data['title']),
                                         text=str(req.data['text_content']))
    new_bulletin.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                        message='Post new bulletin successfully')
