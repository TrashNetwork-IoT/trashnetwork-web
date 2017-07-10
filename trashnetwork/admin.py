from django.contrib import admin

from .models import *

# Add all models here to show on admin page

admin.site.register(RecyclePoint)
admin.site.register(RecycleAccount)
admin.site.register(RecycleCreditRecord)
admin.site.register(RecycleCleaningRecord)
admin.site.register(Feedback)
admin.site.register(Order)


class EventImgAdminModel(admin.ModelAdmin):
    readonly_fields = ['event_image_preview']

admin.site.register(Event, EventImgAdminModel)


class CommodityAdminModel(admin.ModelAdmin):
    readonly_fields = ['commodity_thumbnail_preview']

admin.site.register(Commodity, CommodityAdminModel)


class CommodityImageAdminModel(admin.ModelAdmin):
    readonly_fields = ['commodity_image_preview']

admin.site.register(CommodityImage, CommodityImageAdminModel)
