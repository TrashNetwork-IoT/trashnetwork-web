"""trashnetwork URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from trashnetwork.view.v1.mobile import account as mobile_account

urlpatterns = [
    # Mobile
    url(r'^mobile/account/login', mobile_account.login),
    url(r'^mobile/account/logout', mobile_account.logout),
    url(r'^mobile/account/check_login/(?P<user_id>[0-9]+)', mobile_account.check_login),
    url(r'^mobile/account/user_info/by_id/(?P<user_id>[0-9]+)',
        mobile_account.get_user_info_by_id),
    url(r'^mobile/account/all_group_users', mobile_account.get_all_group_users),
]
