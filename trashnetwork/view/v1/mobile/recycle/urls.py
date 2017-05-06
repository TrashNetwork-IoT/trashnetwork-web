from django.conf.urls import url
from trashnetwork.view.v1.mobile.recycle import account as mobile_account
from trashnetwork.view.v1.mobile.recycle import feedback, credit_record, recycle_point, recycle_record, credit_rank

urlpatterns = [
    # Mobile - Recycle - Account
    url(r'^account/register$', mobile_account.register),
    url(r'^account/login$', mobile_account.login),
    url(r'^account/logout$', mobile_account.logout),
    url(r'^account/check_login/(?P<user_id>\d+)$', mobile_account.check_login),
    url(r'^account/self$', mobile_account.self_info),

    # Mobile - Recycle - Feedback
    url(r'^feedback/new_feekback$', feedback.post_feedback),

    # Mobile - Recycle - Credit Record
    url(r'^credit/record/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_record.get_credit_records),
    url(r'^credit/record/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_record.get_credit_records),
    url(r'^credit/record/(?P<limit_num>\d+)$', credit_record.get_credit_records),
    url(r'^credit/record/new/bottle_recycle$', credit_record.recycle_bottle),

    # Mobile - Recycle - Recycle Point
    url(r'^recycle_point/all_points$', recycle_point.get_all_recycle_points),

    # Mobile - Recycle - Recycle Record
    url(r'^recycle_record/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', recycle_record.get_recycle_record),
    url(r'^recycle_record/(?P<end_time>\d+)/(?P<limit_num>\d+)$', recycle_record.get_recycle_record),
    url(r'^recycle_record/(?P<limit_num>\d+)$', recycle_record.get_recycle_record),
    url(r'^recycle_record/new_record', recycle_record.post_recycle_record),

    # Mobile - Recycle - Credit Rank
    url(r'^credit_rank/day', credit_rank.get_daily_credit_rank),
    url(r'^credit_rank/week', credit_rank.get_weekly_credit_rank),
]
