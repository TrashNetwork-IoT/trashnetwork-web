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
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from trashnetwork import settings

urlpatterns = [
    url(r'^%s' % settings.ADMIN_URL, admin.site.urls),
    # API v1
    url(r'^trashnetwork/v1/', include('trashnetwork.view.v1.urls')),
] + static('trashnetwork/events/', document_root='trashnetwork/events') \
  + static('trashnetwork/commodities/', document_root='trashnetwork/commodities')
