from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from trashnetwork.models import Account
from trashnetwork.view.check_exception import CheckException
from trashnetwork.view import result_code
from trashnetwork.util import view_utils
from trashnetwork.view import authentication

CACHE_KEY_MOBILE_TOKEN_PREFIX = 'mobile_token_'
MOBILE_TOKEN_VALID_HOURS = 120


def token_check(req: Request, permission_limit: str = None):
    try:
        token = req.META['HTTP_AUTH_TOKEN']
        user_id = authentication.parse_token(token)
    except Exception:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(user_id))
    if token != cache_token:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache.set(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(user_id), cache_token, MOBILE_TOKEN_VALID_HOURS * 3600)
    if permission_limit is not None:
        user = Account.objects.filter(user_id=user_id).get()
        if user.account_type != permission_limit:
            raise CheckException(status=status.HTTP_403_FORBIDDEN, result_code=status.HTTP_403_FORBIDDEN,
                                 message=_('Permission denied'))
    else:
        user = Account(user_id=user_id)
    return user


@api_view(['PUT'])
def login(request: Request):
    try:
        account = Account.objects.filter(phone_number=request.data['phone_number']).get()
        if not account.password == request.data['password']:
            raise CheckException(result_code=result_code.MOBILE_LOGIN_INCORRECT_PASSWORD,
                                 message=_('Incorrect password'), status=status.HTTP_401_UNAUTHORIZED)
        token_str = authentication.generate_token(account.user_id)
        cache.set(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(account.user_id), token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
        res = view_utils.get_json_response(result_code=result_code.SUCCESS, message=_('Login successfully'),
                                           status=status.HTTP_201_CREATED, token=token_str)
        return res
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_LOGIN_USER_NOT_EXIST, message=_('User does not exist'),
                             status=status.HTTP_401_UNAUTHORIZED)


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
    cache.delete(CACHE_KEY_MOBILE_TOKEN_PREFIX + str(user.user_id))
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_user_info_by_id(req: Request, user_id: str):
    user = token_check(req=req)
    try:
        user = Account.objects.filter(user_id=int(user_id)).get()
        return view_utils.get_json_response(user=view_utils.get_user_info_dict(user=user))
    except Account.DoesNotExist:
        raise CheckException(result_code=result_code.MOBILE_USER_INFO_NOT_FOUND, message=_('User does not exist'),
                             status=status.HTTP_404_NOT_FOUND)
