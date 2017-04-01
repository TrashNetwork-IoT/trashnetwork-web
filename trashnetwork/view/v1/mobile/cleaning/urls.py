from django.conf.urls import url
from trashnetwork.view.v1.mobile.cleaning import account as mobile_account
from trashnetwork.view.v1.mobile.cleaning import group as mobile_group
from trashnetwork.view.v1.mobile.cleaning import work_record

urlpatterns = [
    # Mobile - Cleaning - Account
    url(r'^account/login$', mobile_account.login),
    url(r'^account/logout$', mobile_account.logout),
    url(r'^account/check_login/(?P<user_id>\d+)$', mobile_account.check_login),
    url(r'^account/user_info/by_id/(?P<user_id>\d+)$', mobile_account.get_user_info_by_id),
    url(r'^account/all_group_users$', mobile_account.get_all_group_users),

    # Mobile - Cleaning - Group
    url(r'^group/all_groups$', mobile_group.all_groups),
    url(r'^group/bulletin/(?P<group_id>\d+)/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', mobile_group.bulletin),
    url(r'^group/bulletin/(?P<group_id>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', mobile_group.bulletin),
    url(r'^group/bulletin/(?P<group_id>\d+)/(?P<limit_num>\d+)$', mobile_group.bulletin),
    url(r'^group/new_bulletin$', mobile_group.post_bulletin),

    # Mobile - Cleaning - Work Record
    url(r'^work/record/by_trash/(?P<trash_id>\d+)/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),
    url(r'^work/record/by_trash/(?P<trash_id>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),
    url(r'^work/record/by_trash/(?P<trash_id>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),

    url(r'^work/record/by_user/(?P<user_id>\d+)/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),
    url(r'^work/record/by_user/(?P<user_id>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),
    url(r'^work/record/by_user/(?P<user_id>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),

    url(r'^work/record/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),
    url(r'^work/record/(?P<end_time>\d+)/(?P<limit_num>\d+)$', work_record.get_work_record),
    url(r'^work/record/(?P<limit_num>\d+)$', work_record.get_work_record),

    url(r'^work/new_record$', work_record.post_work_record)
]
