from django.contrib import admin

from .models import *

# Add all models here to show on admin page

admin.site.register(RecyclePoint)
admin.site.register(RecycleAccount)
admin.site.register(RecycleCreditRecord)
admin.site.register(RecycleCleaningRecord)
admin.site.register(Feedback)


class EventImgAdminModel(admin.ModelAdmin):
    fields = []
    readonly_fields = ['event_image_preview']

    for f in Event._meta.get_fields():
        if isinstance(f, (models.BinaryField, models.DateTimeField)):
            continue
        if f.name == 'id':
            continue
        fields.append(f.name)
    fields.append('event_image_preview')

admin.site.register(Event, EventImgAdminModel)
