"""v22 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from v22 import views
from django.urls import re_path, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path(r'favicon.ico', RedirectView.as_view(url=r'static/favicon.ico')),
    re_path(r'^$', views.welcome),
    path(r'info/<int:info_id>/', views.info),
    path('find', views.search),
    path('try_one', views.try_one),
]
