import json

from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.response import Response

from trashnetwork.models import RecycleAccount
from trashnetwork import models
from trashnetwork.view import authentication, result_code
from trashnetwork.view.check_exception import CheckException
from trashnetwork.util import view_utils
from django.utils.translation import ugettext as _

CACHE_KEY_MOBILE_RECYCLE_TOKEN_PREFIX = 'mobile_recycle_token/'
MOBILE_TOKEN_VALID_HOURS = 168
MOBILE_CLIENT_TYPE_RECYCLE = 'mobile_recycle'


def token_check(req: Request, permission_limit: str = None, optional: bool = False):
    try:
        token = req.META.get('HTTP_AUTH_TOKEN')
        if token is None:
            if optional:
                return None
            raise Exception
        token_json = authentication.parse_token(token)
        user_id = int(token_json['user_id'])
    except Exception:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache_token = cache.get(CACHE_KEY_MOBILE_RECYCLE_TOKEN_PREFIX + str(user_id))
    if token != cache_token or token_json['mobile_type'] != MOBILE_CLIENT_TYPE_RECYCLE:
        raise CheckException(status=status.HTTP_401_UNAUTHORIZED, result_code=status.HTTP_401_UNAUTHORIZED,
                             message=_('Invalid token'))
    cache.set(CACHE_KEY_MOBILE_RECYCLE_TOKEN_PREFIX + str(user_id), cache_token, MOBILE_TOKEN_VALID_HOURS * 3600)
    if permission_limit is not None:
        user = RecycleAccount.objects.filter(user_id=user_id).get()
        if user.account_type != permission_limit:
            raise CheckException(status=status.HTTP_403_FORBIDDEN, result_code=status.HTTP_403_FORBIDDEN,
                                 message=_('Permission denied'))
    else:
        user = RecycleAccount(user_id=user_id)
    return user


def login_response(user: RecycleAccount, message: str):
    token_str = authentication.generate_token(user_id=user.user_id, mobile_type=MOBILE_CLIENT_TYPE_RECYCLE)
    cache.set(CACHE_KEY_MOBILE_RECYCLE_TOKEN_PREFIX + str(user.user_id), token_str, MOBILE_TOKEN_VALID_HOURS * 3600)
    res = view_utils.get_json_response(result_code=result_code.SUCCESS, message=message,
                                       status=status.HTTP_201_CREATED, token=token_str,
                                       user=view_utils.get_recycle_user_basic_info_dict(user=user))
    return res


@api_view(['POST'])
def register(request: Request):
    if len(request.data['password']) < 6 or len(request.data['password']) > 20:
        raise CheckException(result_code=result_code.MR_ILLEGAL_PASSWORD_LENGTH,
                             message=_('Password is too short or too long'))
    try:
        email = request.data['email']
        validate_email(email)
    except ValidationError:
        raise CheckException(result_code=result_code.MR_ILLEGAL_EMAIL_ADDR,
                             message=_('Illegal email address'))
    account_type = request.data['account_type']
    if account_type != models.RECYCLE_ACCOUNT_NORMAL_USER and \
       account_type != models.RECYCLE_ACCOUNT_GARBAGE_COLLECTOR:
        raise CheckException(result_code=result_code.MR_ILLEGAL_ACCOUNT_TYPE,
                             message=_('Illegal account type'))
    if RecycleAccount.objects.filter(user_name=request.data['user_name']):
        raise CheckException(result_code=result_code.MR_USER_NAME_USED,
                             message=_('User name has been used'))
    new_user = RecycleAccount(user_name=request.data['user_name'], password=request.data['password'],
                              account_type=account_type, email=email, credit=0)
    new_user.save()
    return login_response(user=new_user, message=_('Sign up successfully'))


@api_view(['PUT'])
def login(request: Request):
    try:
        account = RecycleAccount.objects.filter(user_name=request.data['user_name']).get()
    except (ValueError, RecycleAccount.DoesNotExist):
        raise CheckException(result_code=result_code.MR_LOGIN_USER_NOT_EXIST, message=_('User does not exist'),
                             status=status.HTTP_401_UNAUTHORIZED)

    if not account.password == request.data['password']:
        raise CheckException(result_code=result_code.MR_LOGIN_INCORRECT_PASSWORD,
                             message=_('Incorrect password'), status=status.HTTP_401_UNAUTHORIZED)
    return login_response(user=account, message=_('Login successfully'))


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
    cache.delete(CACHE_KEY_MOBILE_RECYCLE_TOKEN_PREFIX + str(user.user_id))
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def self_info(req: Request):
    user = token_check(req=req)
    user = RecycleAccount.objects.filter(user_id=user.user_id).get()
    return view_utils.get_json_response(
        user=view_utils.get_recycle_user_basic_info_dict(user=user)
    )


@api_view(['GET'])
def get_delivery_addr(req: Request):
    user = token_check(req=req)
    user = RecycleAccount.objects.filter(user_id=user.user_id).get()
    if not user.delivery_address:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_DELIVER_ADDRESS_NOT_FOUND,
                             message=_('Delivery address not found'))
    try:
        addr_list = json.loads(user.delivery_address)
        if not isinstance(addr_list, list) or len(addr_list) == 0:
            raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_DELIVER_ADDRESS_NOT_FOUND,
                                 message=_('Delivery address not found'))
        return view_utils.get_json_response(address_list=addr_list)
    except json.JSONDecodeError:
        raise CheckException(status=status.HTTP_404_NOT_FOUND, result_code=result_code.MR_DELIVER_ADDRESS_NOT_FOUND,
                             message=_('Delivery address not found'))


@api_view(['PUT'])
def set_new_delivery_addr(req: Request):
    user = token_check(req=req)
    user = RecycleAccount.objects.filter(user_id=user.user_id).get()
    data_addr_list = req.data['new_addr_list']
    if not isinstance(data_addr_list, list):
        raise ParseError()
    for addr in data_addr_list:
        if not isinstance(addr, dict):
            raise ParseError()
        if not 'name' in addr or not 'phone_number' in addr or not 'address' in addr:
            raise ParseError()
        if not str(addr['phone_number']).isdigit():
            raise CheckException(result_code=result_code.MR_ILLEGAL_PHONE, message=_('Illegal phone number'))
    user.delivery_address = json.dumps(data_addr_list)
    user.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                        message=_('Save new delivery address successfully'))
