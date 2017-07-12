from admin_tools.menu import DefaultMenu, items
from django.contrib import admin
from django.contrib.auth import models as auth_model
from django.contrib.auth import admin as auth_admin
from django.conf.urls import url
from django.template import RequestContext
from django.utils.translation import ugettext as _
from trashnetwork.view.admin import push_console
from trashnetwork import settings


class CustomAdminSite(admin.AdminSite):
    site_title = _('TrashNetwork Administration')
    site_header = site_title

    def get_urls(self):
        url_patterns = super(CustomAdminSite, self).get_urls()
        return url_patterns + [
            url(r'^push_console$', push_console.push_console_view),
            url(r'^push_console/api/push_notification', push_console.push_notification)
        ]


site = CustomAdminSite()
site.register(auth_model.User, auth_admin.UserAdmin)
site.register(auth_model.Group, auth_admin.GroupAdmin)


class CustomMenu(DefaultMenu):
    def init_with_context(self, context: RequestContext):
        DefaultMenu.init_with_context(self, context)
        if context.request.user.is_superuser:
            self.children += [
                items.MenuItem(_('Tools'),
                               children=[
                                   items.MenuItem(_('Push Console'), '/%spush_console' % settings.ADMIN_URL),
                               ]
                               ),
            ]
