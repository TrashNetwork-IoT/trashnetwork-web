from django.conf.urls import url
from trashnetwork.view.v1.mobile.cleaning import account as mobile_account

urlpatterns = [
    # Mobile - Cleaning - Account
    url(r'^account/login$', mobile_account.login),
    url(r'^account/logout$', mobile_account.logout),
    url(r'^account/check_login/(?P<user_id>\d+)$', mobile_account.check_login),
    url(r'^account/user_info/by_id/(?P<user_id>\d+)$', mobile_account.get_user_info_by_id),
    url(r'^account/all_group_users$', mobile_account.get_all_group_users),
]
