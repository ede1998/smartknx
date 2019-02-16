"""website URL Configuration

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
from django.urls import path
from . import views
from . import configuration
from functools import partial

urlpatterns = [
    path('', views.navigation, name='root'),
]

for area in configuration.children:
    urlpatterns.append(path(area.url, partial(views.navigation, area=area), name=area.id))
    for subarea in area.children:
        url = area.url + '/' + subarea.url
        urlpatterns.append(path(url, partial(views.details, area=subarea), name=subarea.id))
