from django.conf.urls import url

from trashnetwork.view.v1.mobile.recycle import account as mobile_account
from trashnetwork.view.v1.mobile.recycle import \
    feedback, \
    credit_record, \
    recycle_point, \
    recycle_record, \
    credit_rank, \
    event, \
    credit_mall
from trashnetwork.models import ORDER_IN_PROGRESS, ORDER_FINISHED, ORDER_CANCELLED

urlpatterns = [
    # Mobile - Recycle - Account
    url(r'^account/register$', mobile_account.register),
    url(r'^account/login$', mobile_account.login),
    url(r'^account/logout$', mobile_account.logout),
    url(r'^account/check_login/(?P<user_id>\d+)$', mobile_account.check_login),
    url(r'^account/self$', mobile_account.self_info),
    url(r'^account/delivery_address$', mobile_account.get_delivery_addr),
    url(r'^account/delivery_address/new', mobile_account.set_new_delivery_addr),

    # Mobile - Recycle - Feedback
    url(r'^feedback/new_feedback$', feedback.post_feedback),

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

    # Mobile - Recycle - Event
    url(r'^event/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', event.get_events),
    url(r'^event/(?P<end_time>\d+)/(?P<limit_num>\d+)$', event.get_events),
    url(r'^event/(?P<limit_num>\d+)$', event.get_events),

    # Mobile - Recycle - Credit Mall
    url(r'^credit_mall/commodity/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_mall.get_commodities),
    url(r'^credit_mall/commodity/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_mall.get_commodities),
    url(r'^credit_mall/commodity/(?P<limit_num>\d+)$', credit_mall.get_commodities),
    url(r'^credit_mall/commodity/by_keyword/(?P<keyword>.*?)/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_mall.get_commodities),
    url(r'^credit_mall/commodity/by_keyword/(?P<keyword>.*?)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_mall.get_commodities),
    url(r'^credit_mall/commodity/by_keyword/(?P<keyword>.*?)/(?P<limit_num>\d+)$', credit_mall.get_commodities),
    url(r'^credit_mall/order/new', credit_mall.new_order),

    url(r'^credit_mall/order/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_mall.get_orders),
    url(r'^credit_mall/order/(?P<end_time>\d+)/(?P<limit_num>\d+)$', credit_mall.get_orders),
    url(r'^credit_mall/order/(?P<limit_num>\d+)$', credit_mall.get_orders),
    url(r'^credit_mall/order/by_status/in_progress/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_IN_PROGRESS)),
    url(r'^credit_mall/order/by_status/in_progress/(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_IN_PROGRESS)),
    url(r'^credit_mall/order/by_status/in_progress/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_IN_PROGRESS)),
    url(r'^credit_mall/order/by_status/finished/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_FINISHED)),
    url(r'^credit_mall/order/by_status/finished/(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_FINISHED)),
    url(r'^credit_mall/order/by_status/finished/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_FINISHED)),
    url(r'^credit_mall/order/by_status/cancelled/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_CANCELLED)),
    url(r'^credit_mall/order/by_status/cancelled/(?P<end_time>\d+)/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_CANCELLED)),
    url(r'^credit_mall/order/by_status/cancelled/(?P<limit_num>\d+)$',
        credit_mall.get_orders,
        dict(order_status=ORDER_CANCELLED)),
]
