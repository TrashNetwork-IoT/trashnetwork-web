from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from django.utils.translation import ugettext as _
from json import dumps as to_json

from trashnetwork import models
from trashnetwork.view import result_code
from trashnetwork.util import view_utils
from trashnetwork.view.check_exception import CheckException
from trashnetwork.view.v1.mobile.recycle.account import token_check


@api_view(['GET'])
def get_commodities(req: Request, keyword: str = None, start_time: str = None, end_time: str = None, limit_num: str = None):
    commodity_list = []
    for e in models.Commodity.objects.filter(view_utils.general_query_time_limit(end_time=end_time, start_time=start_time, title__contains=keyword))[:int(limit_num)]:
        commodity_list.append(view_utils.get_model_dict(e, excluded_fields=['description', 'stock', 'quantity_limit', 'type']))
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
        for image in models.CommodityImage.objects.filter(commodity_id=commodity_id):
            commodity_images.append(view_utils.get_encoded_file(image))

        e = models.Commodity.objects.get(commodity_id=commodity_id)
        commodity = view_utils.get_model_dict(e, excluded_fields=['thumbnail'], modify_fields=dict(commodity_type='type'))
        commodity['commodity_images'] = commodity_images

        return view_utils.get_json_response(commodity)
    except models.Commodity.DoesNotExist:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_COMMODITY_NOT_FOUND,
                             message=_('Commodity not found'))


@api_view(['POST'])
def new_order(req: Request):
    user = token_check(req=req)
    user = models.RecycleAccount.objects.filter(user_id=user.user_id).get()
    order = models.Order(buyer=user)

    try:
        order.commodity = models.Commodity.objects.get(id=int(req.data['commodity_id']))
    except models.Commodity.DoesNotExist:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_COMMODITY_NOT_FOUND,
                             message=_('Commodity not found'))

    if order.commodity.commodity_type == models.COMMODITY_TYPE_PHYSICAL:
        if 'delivery_address' not in req.data:
            raise ParseError()
        addr = req.data['delivery_address']
        if not 'name' in addr or not 'phone_number' in addr or not 'address' in addr:
            raise ParseError()
        if not str(addr['phone_number']).isdigit():
            raise CheckException(result_code=result_code.MR_ILLEGAL_PHONE, message=_('Illegal phone number'))
        order.delivery_address = to_json(addr)

    order.quantity = int(req.data['quantity'])
    if order.quantity > order.commodity.stock:
        raise CheckException(status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                             result_code=result_code.MR_INSUFFICIENT_STOCK,
                             message=_('Insufficient stock'))
    if order.quantity > order.commodity.quantity_limit:
        raise CheckException(status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                             result_code=result_code.MR_QUANTITY_EXCEEDS_LIMIT,
                             message=_('Quantity exceeds limit'))
    if order.commodity.credit * order.quantity > user.credit:
        raise CheckException(status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                             result_code=result_code.MR_INSUFFICIENT_CREDIT,
                             message=_('Insufficient credit'))

    order.order_id = timezone.datetime.now().strftime('CM%Y%m%d%H%M%S%f')

    if 'remark' in req.data:
        order.remark = req.data['remark']

    order.save()
    new_credit_record = models.RecycleCreditRecord(user=user,
                                                   item_description='Exchange commodity %s x %d' %
                                                                    (order.commodity.title, order.quantity),
                                                   credit=order.commodity.credit * order.quantity)
    new_credit_record.save()
    user.credit += new_credit_record.credit
    user.save()


@api_view(['GET'])
def get_orders(req: Request, order_status: str = None, start_time: str = None, end_time: str = None, limit_num: str = None):
    order_list = []
    for e in models.Order.objects.filter(view_utils.general_query_time_limit(end_time=end_time, start_time=start_time, status=order_status))[:int(limit_num)]:
        order = view_utils.get_model_dict(e, excluded_fields=['buyer'])
        order['title'] = e.commodity.title
        order['credit'] = e.commodity.credit
        order_list.append(order)
    if len(order_list) == 0:
        raise CheckException(status=status.HTTP_404_NOT_FOUND,
                             result_code=result_code.MR_ORDER_NOT_FOUND,
                             message=_('Commodity not found'))
    return view_utils.get_json_response(commodity_list=order_list)
