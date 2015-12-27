from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(

    '',
    url(r'^$', 'cal.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout$', 'cal.views.logout_view', name='logout_view'),
    url(r'^auth/google', 'cal.views.google_auth', name='google_auth'),
    url(r'^login/google', 'cal.views.login_google', name='login_google'),

    # Django REST framework
    url(r'^', include('api.urls')),

)
