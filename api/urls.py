from api import views
from django.conf.urls import patterns, url

urlpatterns = patterns(

    url(r'^v1/gevents/$', views.GEventList.as_view()),
    url(r'^v1/stats/$', views.StatisticList.as_view()),

)
