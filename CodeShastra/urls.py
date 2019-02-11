"""be URL Configuration

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

from app.views import index, chart, trying, render_sports_page, render_politics_page, render_gen_sports_page, render_gen_politics_page, context_qa, response

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name="index"),
    # url('get_news/', get_news, name="get_news"),
    url(r'^chart/', chart, name="linechart"),
    url(r'^trying/', trying, name="trying"),
    url(r'^sports/', render_sports_page, name="render_sports_page"),
    url(r'^politics/', render_politics_page, name="render_politics_page"),
    url(r'^gen-sports/', render_gen_sports_page, name="render_gen_politics_page"),
    url(r'^gen-politics/', render_gen_politics_page, name="render_gen_politics_page"),
    url(r'^context_qa/', context_qa, name="context_qa"),
    url(r'^response/', response, name="response")
]
