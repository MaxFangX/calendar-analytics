from api import views
from django.conf.urls import include, patterns, url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(

    url(r'^v1/$', views.api_root),
    url(r'^v1/sync/$', views.sync),

    url(r'^v1/gevents/$', views.GEventList.as_view()),
    url(r'^v1/colorcategories/$', views.ColorCategoryList.as_view()),
    url(r'^v1/stats/$', views.StatisticList.as_view()),
    url(r'^v1/tags/$', views.TagList.as_view()),
    url(r'^v1/tags/(?P<pk>[0-9]+)/?$', views.TagDetail.as_view()),

)

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/$', include('rest_framework.urls', namespace='rest_framework')),
]
