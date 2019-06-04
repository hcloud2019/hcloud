from django.contrib import admin
from django.conf.urls import url, include
from django.contrib.auth import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    url(r'^restapi/', include('restful.urls')),
    url(r'^', include('website.urls')),

    url(r'^accounts/login/$', views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
]

