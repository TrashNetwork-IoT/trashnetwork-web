from django.conf.urls import url
from trashnetwork.view.v1.mobile.recycle import account as mobile_account
from trashnetwork.view.v1.mobile.recycle import feedback

urlpatterns = [
    # Mobile - Recycle - Account
    url(r'^account/register$', mobile_account.register),
    url(r'^account/login$', mobile_account.login),
    url(r'^account/logout$', mobile_account.logout),
    url(r'^account/check_login/(?P<user_id>\d+)$', mobile_account.check_login),
    url(r'^account/self$', mobile_account.self_info),

    # Mobile - Recycle - Feedback
    url(r'^feedback/new_feekback', feedback.post_feedback)
]
