from django.conf.urls import url
from trashnetwork.view.v1.mobile.cleaning import account as mobile_account

urlpatterns = [
    # Mobile - Cleaning
    url(r'^cleaning/account/login', mobile_account.login),
    url(r'^cleaning/account/logout', mobile_account.logout),
    url(r'^cleaning/account/check_login/(?P<user_id>[0-9]+)', mobile_account.check_login),
    url(r'^cleaning/account/user_info/by_id/(?P<user_id>[0-9]+)',
        mobile_account.get_user_info_by_id),
    url(r'^cleaning/account/all_group_users', mobile_account.get_all_group_users),
]
