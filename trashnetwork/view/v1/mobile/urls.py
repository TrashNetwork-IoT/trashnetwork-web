from django.conf.urls import url, include

from trashnetwork.view.v1.mobile import public

urlpatterns = [
    # Mobile - Cleaning
    url(r'^cleaning/', include('trashnetwork.view.v1.mobile.cleaning.urls')),

    # Mobile - Recycle
    url(r'^recycle/', include('trashnetwork.view.v1.mobile.recycle.urls')),

    # Mobile - Public
    url(r'^public/trash/all_trashes$', public.all_trashes),
    url(r'^public/feedback/feedbacks/(?P<start_time>\d+)/(?P<end_time>\d+)/(?P<limit_num>\d+)$', public.get_feedback),
    url(r'^public/feedback/feedbacks/(?P<end_time>\d+)/(?P<limit_num>\d+)$', public.get_feedback),
    url(r'^public/feedback/feedbacks/(?P<limit_num>\d+)$', public.get_feedback),
]
