from django.contrib import admin

from .models import *

# Add all models here to show on admin page

admin.site.register(RecyclePoint)
admin.site.register(RecycleAccount)
admin.site.register(RecycleCreditRecord)
admin.site.register(RecycleCleaningRecord)
admin.site.register(Feedback)