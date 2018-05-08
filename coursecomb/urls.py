"""test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.contrib import admin
from courses import views
import django_cas_ng.views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.landing, name='landing'),
	url(r'^home/$', login_required(views.home)),
	url(r'^api/get_courses/', login_required(views.get_courses), name='get_courses'),
    url(r'^favorites/', login_required(views.favorites), name='favorites'),
    url(r'^about/', login_required(views.about), name='about'),
    url(r'^feedback/', login_required(views.feedback), name='feedback'),
    url(r'^admin/', admin.site.urls),
    url(r'accounts/login/$', django_cas_ng.views.login, name='cas_ng_login'),
    url(r'accounts/logout/$', django_cas_ng.views.logout, name='cas_ng_logout', )
]