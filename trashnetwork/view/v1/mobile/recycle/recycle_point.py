from rest_framework.decorators import api_view
from rest_framework.request import Request

from trashnetwork import models
from trashnetwork.view.v1.mobile.recycle import account
from trashnetwork.util import view_utils


@api_view(['GET'])
def get_all_recycle_points(req: Request):
    user = account.token_check(req=req, optional=True)
    if user is not None:
        user = models.RecycleAccount.objects.filter(user_id=user.user_id).get()
    result_list = []
    for rp in models.RecyclePoint.objects.all():
        if user is not None and user.account_type == models.RECYCLE_ACCOUNT_GARBAGE_COLLECTOR:
            result_list.append(view_utils.get_recycle_point_dict(point=rp, is_owner=True))
        else:
            result_list.append(view_utils.get_recycle_point_dict(point=rp, is_owner=False))
    return view_utils.get_json_response(recycle_point_list=result_list)
