from django.contrib import admin
from jsoneditor.forms import JSONEditor
from .models import *

# Add all models here to show on admin page


class CustomModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        DummyJsonField: {'widget': JSONEditor()},
    }


class RecyclePointModelAdmin(CustomModelAdmin):
    readonly_fields = ['point_id']
    raw_id_fields = ['owner']
    search_fields = ['point_id', 'description', 'owner__user_name']


admin.site.register(RecyclePoint, RecyclePointModelAdmin)


class RecycleAccountModelAdmin(CustomModelAdmin):
    readonly_fields = ['user_id']
    list_filter = ['account_type']
    search_fields = ['user_name']


admin.site.register(RecycleAccount, RecycleAccountModelAdmin)


class RecycleCreditRecordModelAdmin(CustomModelAdmin):
    raw_id_fields = ['user']
    search_fields = ['item_description', 'user__user_name']


admin.site.register(RecycleCreditRecord, RecycleCreditRecordModelAdmin)


class RecycleCleaningRecordModelAdmin(CustomModelAdmin):
    raw_id_fields = ['user']
    search_fields = ['user__user_name', 'recycle_point__point_id', 'recycle_point__description']


admin.site.register(RecycleCleaningRecord, RecycleCleaningRecordModelAdmin)


class FeedbackModelAdmin(CustomModelAdmin):
    search_fields = ['title', 'poster__user_name', 'text']
    raw_id_fields = ['poster']


admin.site.register(Feedback, FeedbackModelAdmin)


class EventImgModelAdmin(CustomModelAdmin):
    readonly_fields = ['event_image_preview']
    search_fields = ['title', 'url', 'digest']


admin.site.register(Event, EventImgModelAdmin)


class CommodityModelAdmin(CustomModelAdmin):
    readonly_fields = ['description_preview', 'commodity_thumbnail_preview', 'commodity_images_preview']
    list_filter = ['commodity_type']
    search_fields = ['title', 'description']


admin.site.register(Commodity, CommodityModelAdmin)


class CommodityImageModelAdmin(CustomModelAdmin):
    readonly_fields = ['commodity_image_preview']
    raw_id_fields = ['commodity']
    search_fields = ['commodity__title', 'commodity__description']


admin.site.register(CommodityImage, CommodityImageModelAdmin)


class OrderModelAdmin(CustomModelAdmin):
    readonly_fields = ['order_id']
    list_filter = ['status']
    raw_id_fields = ['buyer']
    search_fields = ['order_id', 'buyer__user_name', 'title']


admin.site.register(Order, OrderModelAdmin)
