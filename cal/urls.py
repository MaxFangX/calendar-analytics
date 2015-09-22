from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(

    '',
    url(r'^$', 'cal.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login$', 'cal.views.login_view', name='login_view'),
    url(r'^logout$', 'cal.views.logout_view', name='logout_view'),
    url(r'^auth/google', 'cal.views.google_auth', name='google_auth')

)
