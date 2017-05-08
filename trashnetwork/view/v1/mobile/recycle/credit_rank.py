import datetime

from requests import Request
from rest_framework.decorators import api_view

from trashnetwork import models
from trashnetwork.util import view_utils
from trashnetwork.view.v1.mobile.recycle import account

daily_credit_rank_list = []
daily_credit_rank_list_update_time = datetime.datetime.now()
weekly_credit_rank_list = []
weekly_credit_rank_list_update_time = datetime.datetime.now()

RANK_LIST_TYPE_WEEKLY = 'weekly'
RANK_LIST_TYPE_DAILY = 'daily'


def update_rank_list(rank_list_type: str = RANK_LIST_TYPE_DAILY):
    now = datetime.datetime.now()
    if rank_list_type == RANK_LIST_TYPE_DAILY:
        global daily_credit_rank_list
        global daily_credit_rank_list_update_time
        rank_list = daily_credit_rank_list
        daily_credit_rank_list_update_time = datetime.datetime.now()
        start_time = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        end_time = int(now.replace(hour=23, minute=59, second=59, microsecond=10**6-1).timestamp())
    elif rank_list_type == RANK_LIST_TYPE_WEEKLY:
        global weekly_credit_rank_list
        global weekly_credit_rank_list_update_time
        rank_list = weekly_credit_rank_list
        weekly_credit_rank_list_update_time = datetime.datetime.now()
        start_time = int((now - datetime.timedelta(days=now.weekday()))
                         .replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        end_time = int((now + datetime.timedelta(days=6-now.weekday()))
                       .replace(hour=23, minute=59, second=59, microsecond=10**6-1).timestamp())
    else:
        return

    user_credit_dict = {}
    models.RecycleCreditRecord.objects.filter()
    for cr in models.RecycleCreditRecord.objects.filter(credit__gt=0).filter(
            view_utils.general_query_time_limit(start_time=start_time, end_time=end_time)):
        user_name = cr.user.user_name
        user_credit = user_credit_dict.get(user_name)
        if user_credit is None:
            user_credit = cr.credit
        else:
            user_credit = user_credit + cr.credit
        user_credit_dict[user_name] = user_credit
    rank_list.clear()
    for key in user_credit_dict:
        rank_list.append({'user_name': key, 'credit': user_credit_dict[key]})
    rank_list.sort(key=lambda x: x['credit'], reverse=True)
    print('Finish updating %s credit rank list' % rank_list_type)


def get_credit_rank_response(rank_list: list, update_time: datetime.datetime, user_name: str=None, limit_rank: int=50):
    end_index = limit_rank
    while end_index < len(rank_list):
        if rank_list[end_index]['credit'] == rank_list[end_index - 1]['credit']:
            end_index += 1
        else:
            break

    if user_name is None:
        return view_utils.get_json_response(update_time=int(update_time.timestamp()),
                                            rank_list=rank_list[0:end_index])
    else:
        user_rank = -1
        credit = 0
        for rank in rank_list:
            if rank['user_name'] == user_name:
                user_rank = rank_list.index(rank)
                credit = rank['credit']
                while user_rank - 1 >= 0 and rank_list[user_rank - 1]['credit'] == credit:
                    user_rank = user_rank - 1
                user_rank = user_rank + 1
                break
        return view_utils.get_json_response(update_time=int(update_time.timestamp()),
                                            rank=user_rank, credit=credit,
                                            rank_list=rank_list[0:limit_rank])


@api_view(['GET'])
def get_daily_credit_rank(req: Request):
    global daily_credit_rank_list
    global daily_credit_rank_list_update_time
    user = account.token_check(req=req, optional=True)
    user_name = None
    if user is not None:
        user_name = models.RecycleAccount.objects.filter(user_id=user.user_id).get().user_name
    return get_credit_rank_response(rank_list=daily_credit_rank_list, update_time=daily_credit_rank_list_update_time,
                                    user_name=user_name)


@api_view(['GET'])
def get_weekly_credit_rank(req: Request):
    global weekly_credit_rank_list
    global weekly_credit_rank_list_update_time
    user = account.token_check(req=req, optional=True)
    user_name = None
    if user is not None:
        user_name = models.RecycleAccount.objects.filter(user_id=user.user_id).get().user_name
    return get_credit_rank_response(rank_list=weekly_credit_rank_list, update_time=weekly_credit_rank_list_update_time,
                                    user_name=user_name)
