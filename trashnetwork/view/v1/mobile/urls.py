from django.conf.urls import url, include

urlpatterns = [
    # Mobile - Cleaning
    url(r'^cleaning', include('trashnetwork.view.v1.mobile.cleaning.urls')),
]
