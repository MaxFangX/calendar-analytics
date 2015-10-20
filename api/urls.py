from api import views
from django.conf.urls import patterns, url

urlpatterns = patterns(

    url(r'^v1/gevents/$', views.GEventList),
    url(r'^v1/stats/$', views.StatisticList),

)
