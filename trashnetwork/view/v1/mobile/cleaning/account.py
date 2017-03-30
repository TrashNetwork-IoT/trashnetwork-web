from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from trashnetwork.models import CleaningAccount
from trashnetwork.view.check_exception import CheckException
from trashnetwork.view import result_code
from trashnetwork.util import view_utils
from trashnetwork.view import authentication

CACHE_KEY_MOBILE_CLEANING_TOKEN_PREFIX = 'mobile_cleaning_token/'
MOBILE_TOKEN_VALID_HOURS = 120
MOBILE_CLIENT_TYPE_CLEANING = 'mobile_cleaning'


def token_check(req: Request, permission_limit: str = None):
    try:
        token = req.META['HTTP_AUTH_TOKEN']
        token_json = authentication.parse_token(token)
        user_id = token_json['user_id']
    except Exception:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_MOBILE_CLEANING_TOKEN_PREFIX + str(user_id))
    if token != cache_token or token_json['mobile_type'] != MOBILE_CLIENT_TYPE_CLEANING:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache.set(CACHE_KEY_MOBILE_CLEANING_TOKEN_PREFIX + str(user_id), cache_token, MOBILE_TOKEN_VALID_HOURS * 3600)
    if permission_limit is not None:
        user = CleaningAccount.objects.filter(user_id=user_id).get()
        if user.account_type != permission_limit:
            raise CheckException(status=status.HTTP_403_FORBIDDEN, result_code=status.HTTP_403_FORBIDDEN,
                                 message=_('Permission denied'))
    else:
        user = CleaningAccount(user_id=user_id)
    return user


@api_view(['PUT'])
def login(request: Request):
    try:
        account = CleaningAccount.objects.filter(user_id=int(request.data['user_id'])).get()
    except (ValueError, CleaningAccount.DoesNotExist):
        raise CheckException(result_code=result_code.MC_LOGIN_USER_NOT_EXIST, message=_('User does not exist'),
                             status=status.HTTP_401_UNAUTHORIZED)

    if not account.password == request.data['password']:
        raise CheckException(result_code=result_code.MC_LOGIN_INCORRECT_PASSWORD,
                             message=_('Incorrect password'), status=status.HTTP_401_UNAUTHORIZED)
    token_str = authentication.generate_token(user_id=account.user_id, mobile_type=MOBILE_CLIENT_TYPE_CLEANING)
    cache.set(CACHE_KEY_MOBILE_CLEANING_TOKEN_PREFIX + str(account.user_id), token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
    res = view_utils.get_json_response(result_code=result_code.SUCCESS, message=_('Login successfully'),
                                       status=status.HTTP_201_CREATED, token=token_str)
    return res


@api_view(['GET'])
def check_login(req: Request, user_id: str):
    user = token_check(req=req)
    if str(user.user_id) != user_id:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Token does not match this user.'))
    return view_utils.get_json_response()


@api_view(['DELETE'])
def logout(req: Request):
    user = token_check(req=req)
    cache.delete(CACHE_KEY_MOBILE_CLEANING_TOKEN_PREFIX + str(user.user_id))
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_user_info_by_id(req: Request, user_id: str):
    user = token_check(req=req)
    try:
        user = CleaningAccount.objects.filter(user_id=int(user_id)).get()
        return view_utils.get_json_response(user=view_utils.get_cleaning_user_info_dict(user=user))
    except CleaningAccount.DoesNotExist:
        raise CheckException(result_code=result_code.MC_USER_INFO_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_all_group_users(req: Request):
    user = token_check(req=req)
    user_list = []
    for u in CleaningAccount.objects.all():
        if u.user_id == user.user_id:
            continue
        user_list.append(view_utils.get_cleaning_user_info_dict(user=u))
    return view_utils.get_json_response(user_list=user_list)
