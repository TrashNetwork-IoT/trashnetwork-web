import json

from django.contrib import admin
from django.core.checks import messages

from trashnetwork import admin_site
from jsoneditor.forms import JSONEditor
from codemirror2.widgets import CodeMirrorEditor
from django_object_actions import DjangoObjectActions
from django.utils.translation import ugettext as _
from .models import *


# Add all models here to show on admin page


class CustomModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        DummyJsonField: {'widget': JSONEditor()},
        DummyHtmlField: {'widget': CodeMirrorEditor(options={'mode': 'xml',
                                                             'lineNumbers': True,
                                                             'lineWrapping': True
                                                             })}
    }


class RecyclePointModelAdmin(CustomModelAdmin):
    list_display = ['point_id', 'description', 'longitude', 'latitude', 'owner']
    readonly_fields = ['point_id']
    raw_id_fields = ['owner']
    search_fields = ['point_id', 'description', 'owner__user_name']


admin_site.site.register(RecyclePoint, RecyclePointModelAdmin)


class RecycleAccountModelAdmin(CustomModelAdmin):
    list_display = ['user_id', 'user_name', 'account_type']
    readonly_fields = ['user_id']
    list_filter = ['account_type']
    search_fields = ['user_name']


admin_site.site.register(RecycleAccount, RecycleAccountModelAdmin)


class RecycleCreditRecordModelAdmin(CustomModelAdmin):
    list_display = ['user', 'item_description', 'timestamp', 'credit']
    raw_id_fields = ['user']
    readonly_fields = ['timestamp', 'credit']
    search_fields = ['item_description', 'user__user_name']


admin_site.site.register(RecycleCreditRecord, RecycleCreditRecordModelAdmin)


class RecycleCleaningRecordModelAdmin(CustomModelAdmin):
    list_display = ['user', 'recycle_point', 'timestamp']
    raw_id_fields = ['user']
    readonly_fields = ['timestamp']
    search_fields = ['user__user_name', 'recycle_point__point_id', 'recycle_point__description']


admin_site.site.register(RecycleCleaningRecord, RecycleCleaningRecordModelAdmin)


class FeedbackModelAdmin(CustomModelAdmin):
    list_display = ['title', 'poster', 'timestamp']
    search_fields = ['title', 'poster__user_name', 'text']
    readonly_fields = ['timestamp']
    raw_id_fields = ['poster']


admin_site.site.register(Feedback, FeedbackModelAdmin)


class EventModelAdmin(CustomModelAdmin):
    list_display = ['title', 'url', 'timestamp']
    readonly_fields = ['timestamp', 'event_image_preview', 'event_page_link']
    search_fields = ['title', 'url', 'digest']


admin_site.site.register(Event, EventModelAdmin)


class CommodityModelAdmin(CustomModelAdmin):
    list_display = ['title', 'timestamp', 'credit', 'stock']
    readonly_fields = ['timestamp', 'description_preview', 'commodity_thumbnail_preview', 'commodity_images_preview']
    list_filter = ['commodity_type']
    search_fields = ['title', 'description']


admin_site.site.register(Commodity, CommodityModelAdmin)


class CommodityImageModelAdmin(CustomModelAdmin):
    list_display = ['commodity', 'image']
    readonly_fields = ['commodity_image_preview']
    raw_id_fields = ['commodity']
    search_fields = ['commodity__title', 'commodity__description']


admin_site.site.register(CommodityImage, CommodityImageModelAdmin)


class OrderModelAdmin(DjangoObjectActions, CustomModelAdmin):
    list_display = ['title', 'buyer', 'timestamp', 'status']
    readonly_fields = ['order_id', 'buyer', 'credit', 'quantity', 'status', 'timestamp']
    list_filter = ['status']
    raw_id_fields = ['buyer']
    search_fields = ['order_id', 'buyer__user_name', 'title']

    def get_readonly_fields(self, request, order: Order = None):
        if order is not None and (order.status == ORDER_FINISHED or order.status == ORDER_CANCELLED):
            result_field = []
            for f in Order._meta.get_fields():
                result_field += [f.name]
            return result_field
        return self.readonly_fields

    def cancel_order(self, request, order: Order):
        if order.status == ORDER_CANCELLED or order.status == ORDER_FINISHED:
            return self.message_user(request, _('This order cannot be cancelled'), messages.ERROR)
        order.status = ORDER_CANCELLED
        order.save()
        user = order.buyer
        record = RecycleCreditRecord(user=user, credit=order.credit * order.quantity)
        record.item_description = _('Cancelled order "%s x%d"') % (order.title, order.quantity)
        record.save()
        user.credit += order.credit * order.quantity
        user.save()
        if Commodity.objects.filter(commodity_id=order.commodity_id).exists():
            commodity = Commodity.objects.get(commodity_id=order.commodity_id)
            commodity.stock += order.quantity
            commodity.save()
        return self.message_user(request, _('This order has been cancelled'))

    cancel_order.label = _('Cancel Order')

    def deliver_order(self, request, order: Order):
        if order.status != ORDER_IN_PROGRESS:
            return self.message_user(request, _('Only orders with in progress status can be delivered'), messages.ERROR)
        try:
            addr_json = json.loads(order.delivery_address or '{}')
            if not addr_json or 'name' not in addr_json or 'phone_number' not in addr_json or 'address' not in addr_json:
                return self.message_user(request, _('Invalid delivery address'),
                                         messages.ERROR)
        except json.JSONDecodeError:
            return self.message_user(request, _('Invalid delivery address'),
                                     messages.ERROR)
        try:
            delivery_info = json.loads(order.delivery or '{}')
            if not delivery_info or 'company' not in delivery_info or 'waybill_id' not in delivery_info:
                return self.message_user(request, _('Invalid delivery info'),
                                         messages.ERROR)
        except json.JSONDecodeError:
            return self.message_user(request, _('Invalid delivery info'),
                                     messages.ERROR)
        order.status = ORDER_DELIVERING
        order.save()
        return self.message_user(request, _('Deliver successfully'))

    deliver_order.label = _('Delivery')

    def finish_order(self, request, order: Order):
        if order.status == ORDER_FINISHED or order.status == ORDER_CANCELLED:
            return self.message_user(request, _('This order has been already finished or cancelled'), messages.ERROR)
        order.status = ORDER_FINISHED
        order.save()
        return self.message_user(request, _('This order has been finished'))

    finish_order.label = _('Finish order')

    def get_change_actions(self, request, order_id: str, form_url):
        change_actions = super(OrderModelAdmin, self).get_change_actions(request, order_id, form_url)
        change_actions = list(change_actions)
        order = Order.objects.get(order_id=order_id)
        if order.status == ORDER_CANCELLED or order.status == ORDER_FINISHED:
            change_actions.remove('cancel_order')
            change_actions.remove('finish_order')
        if order.status != ORDER_IN_PROGRESS:
            change_actions.remove('deliver_order')
        return change_actions

    change_actions = ['deliver_order', 'finish_order', 'cancel_order']


admin_site.site.register(Order, OrderModelAdmin)
