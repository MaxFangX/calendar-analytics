from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(

    '',
    url(r'^$', 'cal.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', include('loginas.urls')),
    url(r'^logout$', 'cal.views.logout_view', name='logout_view'),
    url(r'^auth/google', 'cal.views.google_auth', name='google_auth'),
    url(r'^auth/clear', 'cal.views.clear_auth', name='clear_auth'),
    url(r'^login/google', 'cal.views.login_google', name='login_google'),
    url(r'^accounts/profile', 'cal.views.accounts_profile', name='accounts_profile'),
    url(r'^add_tag/$', 'cal.views.add_tag', name='add_tag'),
    url(r'^edit_tag/$', 'cal.views.edit_tag', name='edit_tag'),

    # Django REST framework
    url(r'^', include('api.urls')),

    # Python social auth
    url('', include('social.apps.django_app.urls', namespace='social')),

)
