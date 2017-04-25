from django.contrib import admin

from .models import *

# Add all models here to show on admin page

admin.site.register(CleaningAccount)
admin.site.register(Trash)
admin.site.register(CleaningGroup)
admin.site.register(CleaningGroupMembership)
admin.site.register(CleaningGroupBulletin)
admin.site.register(CleaningWorkRecord)
admin.site.register(RecycleAccount)
admin.site.register(RecycleCreditRecord)
admin.site.register(Feedback)