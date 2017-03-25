from api import views
from django.conf.urls import include, patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns(

    url(r'^v1/$', views.api_root),
    url(r'^v1/sync/$', views.sync),

    url(r'^v1/gcalendars/$', views.GCalendarList.as_view()),
    url(r'^v1/gcalendars/(?P<pk>[0-9]+)/toggle-enabled/?$',
        views.GCalendarToggleEnabled.as_view()),
    url(r'^v1/toggle-privacy', views.toggle_privacy),
    url(r'^v1/gevents/$', views.GEventList.as_view()),
    url(r'^v1/categories/$', views.CategoryList.as_view()),
    url(r'^v1/categories/(?P<pk>[0-9]+)/?$', views.CategoryDetail.as_view()),
    url(r'^v1/categories/(?P<pk>[0-9]+)/events/?$', views.CategoryDetailEvents.as_view()),
    url(r'^v1/categories/(?P<pk>[0-9]+)/timeseries/(?P<time_step>\w+)/?$', views.CategoryDetailEventTimeSeries.as_view()),
    url(r'^v1/stats/$', views.StatisticList.as_view()),
    url(r'^v1/tags/$', views.TagList.as_view()),
    url(r'^v1/tags/(?P<pk>[0-9]+)/?$', views.TagDetail.as_view()),
    url(r'^v1/tags/(?P<pk>[0-9]+)/events/?$', views.TagDetailEvents.as_view()),
    url(r'^v1/tags/(?P<pk>[0-9]+)/timeseries/(?P<time_step>\w+)/?$', views.TagDetailEventTimeSeries.as_view()),
    url(r'^v1/tags/(?P<pk>[0-9]+)/by-category/?$', views.TagsByCategories.as_view()),

)

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^api-auth/$', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += staticfiles_urlpatterns()
