from api import views
from django.conf.urls import include, patterns, url
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserList)

urlpatterns = patterns(

    url(r'^v1/', include(router.urls)),

)
