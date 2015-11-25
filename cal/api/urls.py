from api import views
from django.conf.urls import include, patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = patterns(

    url(r'^v1/$', views.api_root),
    url(r'^v1/gevents/$', views.GEventList.as_view()),
    url(r'^v1/stats/$', views.StatisticList.as_view()),
    url(r'^v1/', include(router.urls)),

)

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/$', include('rest_framework.urls', namespace='rest_framework')),
]
