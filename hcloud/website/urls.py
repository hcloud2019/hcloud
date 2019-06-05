from django.conf.urls import url
from django.shortcuts import redirect
from django.contrib.auth import views as auth
from . import views

urlpatterns = [

    # login url
    url(r'^accounts/signup/$', views.signup, name='signup'),
    url(r'^accounts/logout/$', auth.LogoutView.as_view(template_name='website/home.html')),

    # file url
    url(r'^$', views.home, name='home'),
    url(r'^file_search/(?P<file_name>([\w\sㄱ-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/)*)$',
        views.search, name='search'),
    url(r'^list/(?P<path>([\w\sㄱ-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/)*)$',
        views.filelist, name='filelist'),
    url(r'^upload/(?P<path>([\w\sㄱ-ㅣ가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/)*)$',
        views.upload, name='upload'),
    url(r'^view/(?P<path>([\w\sㄱ-ㅣ가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/*)*)$',
        views.view, name='view'),
    url(r'^make_folder/(?P<path>([\w\sㄱ-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/)*)$',
        views.makefolder, name='makefolder'),
    url(
        r'^copy/(?P<old_path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/*)*)&(?P<new_path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]]*/*)*)$',
        views.copy, name='copy'),
    url(
        r'^move/(?P<old_path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/*)*)&(?P<new_path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]]*/*)*)$',
        views.move, name='move'),
    url(r'^delete/(?P<path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/*)*)$',
        views.delete, name='delete'),
    url(r'^download/(?P<path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/*)*)$',
        views.download, name='download'),
]
