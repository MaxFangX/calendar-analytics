from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(

    '',
    url(r'^$|^sync', 'cal.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', include('loginas.urls')),
    url(r'^admin/generate-categories', 'cal.views.generate_categories',
        name='generate_categories'),
    url(r'^logout$', 'cal.views.logout_view', name='logout_view'),
    url(r'^auth/google', 'cal.views.google_auth', name='google_auth'),
    url(r'^auth/clear', 'cal.views.clear_auth', name='clear_auth'),
    url(r'^complete-with-token/(?P<backend>[^/]+)/$',
        'cal.views.complete_with_token', name='complete_with_token'),
    url(r'^accounts/profile', 'cal.views.accounts_profile', name='accounts_profile'),

    url(r'^categories/(?P<pk>[0-9]+)/?', 'cal.views.category_detail', name='category_detail'),
    url(r'^tags/(?P<pk>[0-9]+)/?', 'cal.views.tag_detail', name='tag_detail'),

    # Django REST framework
    url(r'^', include('api.urls')),

    # Python social auth
    url('', include('social.apps.django_app.urls', namespace='social')),

)
