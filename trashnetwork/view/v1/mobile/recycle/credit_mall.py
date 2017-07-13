import json
import threading

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.request import Request
from django.utils.translation import ugettext as _
from json import dumps as to_json

from trashnetwork import models
from trashnetwork.view import result_code
from trashnetwork.util import view_utils
from trashnetwork.view.check_exception import CheckException
from trashnetwork.view.v1.mobile.recycle.account import token_check


@api_view(['GET'])
def get_commodities(req: Request, keyword: str = None, start_time: str = None, end_time: str = None,
                    limit_num: str = None):
    commodity_list = []
    for e in models.Commodity.objects.filter(
            view_utils.general_query_time_limit(end_time=end_time, start_time=start_time, title__icontains=keyword))[
             :int(limit_num)]:
        commodity_list.append(
            view_utils.get_model_dict(e, excluded_fields=['description', 'stock', 'quantity_limit', 'type']))
    if len(commodity_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_COMMODITY_NOT_FOUND,
                             message=_('Commodity not found'))
    return view_utils.get_json_response(commodity_list=commodity_list)


@api_view(['GET'])
def get_commodity_detail(req: Request, commodity_id: str):
    commodity_id = int(commodity_id)
    try:
        commodity_images = []
        for ci in models.CommodityImage.objects.filter(commodity_id=commodity_id):
            commodity_images.append(view_utils.get_encoded_file(ci.image))

        e = models.Commodity.objects.get(commodity_id=commodity_id)
        commodity = view_utils.get_model_dict(e, excluded_fields=['thumbnail'],
                                              modify_fields=dict(commodity_type='type'))
        commodity['commodity_images'] = commodity_images
        return view_utils.get_json_response(commodity=commodity)
    except models.Commodity.DoesNotExist:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_COMMODITY_NOT_FOUND,
                             message=_('Commodity not found'))


commodity_lock_dict = {}
lock_dict_lock = threading.Lock()


@api_view(['POST'])
def new_order(req: Request):
    global lock_dict_lock
    global commodity_lock_dict
    user = token_check(req=req)
    user = models.RecycleAccount.objects.filter(user_id=user.user_id).get()
    order = models.Order(buyer=user)
    order.quantity = int(req.data['quantity'])
    if order.quantity <= 0:
        raise CheckException(result_code=result_code.MR_ILLEGAL_QUANTITY,
                             message=_('Illegal quantity(<=0)'))

    try:
        commodity_id = int(req.data['commodity_id'])
        commodity = models.Commodity.objects.get(commodity_id=commodity_id)
    except models.Commodity.DoesNotExist:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_COMMODITY_NOT_FOUND,
                             message=_('Commodity not found'))

    lock_dict_lock.acquire()
    if str(commodity_id) not in commodity_lock_dict:
        commodity_lock_dict.update({str(commodity_id): threading.Lock()})
    commodity_lock = commodity_lock_dict[str(commodity_id)]
    lock_dict_lock.release()

    commodity_lock.acquire()
    try:
        if commodity.commodity_type == models.COMMODITY_TYPE_PHYSICAL:
            if 'delivery_address' not in req.data:
                raise ParseError()
            addr = req.data['delivery_address']
            if not 'name' in addr or not 'phone_number' in addr or not 'address' in addr:
                raise ParseError()
            if not str(addr['phone_number']).isdigit():
                raise CheckException(result_code=result_code.MR_ILLEGAL_PHONE, message=_('Illegal phone number'))
            order.delivery_address = to_json(addr)

        if order.quantity > commodity.stock:
            raise CheckException(status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                 result_code=result_code.MR_INSUFFICIENT_STOCK,
                                 message=_('Insufficient stock'))
        if order.quantity > commodity.quantity_limit:
            raise CheckException(status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                 result_code=result_code.MR_QUANTITY_EXCEEDS_LIMIT,
                                 message=_('Quantity exceeds limit'))
        if commodity.credit * order.quantity > user.credit:
            raise CheckException(status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                 result_code=result_code.MR_INSUFFICIENT_CREDIT,
                                 message=_('Insufficient credit'))

        commodity.stock -= order.quantity
        commodity.save()

        order.order_id = timezone.datetime.now().strftime('CM%Y%m%d%H%M%S%f')
        order.credit = commodity.credit
        order.title = commodity.title
        order.commodity_id = commodity.commodity_id

        if 'remark' in req.data:
            order.remark = req.data['remark']

        order.save()
        new_credit_record = models.RecycleCreditRecord(user=user,
                                                       item_description='%s x%d' %
                                                                        (commodity.title, order.quantity),
                                                       credit=-(commodity.credit * order.quantity))
        new_credit_record.save()
        user.credit += new_credit_record.credit
        user.save()
    except Exception as e:
        raise e
    finally:
        commodity_lock.release()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, message=_('Submit order successfully'))


@api_view(['GET'])
def get_orders(req: Request, order_status: str = None, start_time: str = None, end_time: str = None,
               limit_num: str = None):
    if order_status is not None and order_status != 'in_progress' and order_status != 'delivering' \
            and order_status != 'cancelled' and order_status != 'finished':
        raise NotFound()
    user = token_check(req=req)
    order_list = []
    for e in models.Order.objects.filter(buyer=user).filter(
            view_utils.general_query_time_limit(end_time=end_time, start_time=start_time, status=order_status))[
             :int(limit_num)]:
        order = view_utils.get_model_dict(e, excluded_fields=['buyer', 'delivery_address', 'delivery'])
        if e.delivery_address:
            order['delivery_address'] = json.loads(e.delivery_address)
        if e.delivery:
            order['delivery'] = json.loads(e.delivery)
        order_list.append(order)
    if len(order_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_ORDER_NOT_FOUND,
                             message=_('Order not found'))
    return view_utils.get_json_response(order_list=order_list)
