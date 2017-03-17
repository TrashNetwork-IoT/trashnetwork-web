from django.conf.urls import url, include

urlpatterns = [
    # Mobile
    url(r'^mobile/', include('trashnetwork.view.v1.mobile.urls')),
]