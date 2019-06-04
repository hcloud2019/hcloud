from django.conf.urls import url
from django.shortcuts import redirect
from rest_framework.urlpatterns import format_suffix_patterns
from .views import FileList
from .views import FileDetail,FileCopyMove

file_regex = '[\w\sㄱ-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]'

urlpatterns = [
    url(r'^list/(?P<path>([\w\sㄱ-ㅣ가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/)*)$', FileList.as_view(), name='file-list'),
    url(r'^file/(?P<path>([\w\sㄱ-ㅣ가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/*)*)$', FileDetail.as_view(), name='file-detail'),
    url(r'^file-mod/(?P<old_path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]*/*)*)&(?P<new_path>([\w\s가-힣.\`\'\˜\=\+\#\ˆ\@\$\&\-\.\(\)\{\}\;\[\]]]*/*)*)$', FileCopyMove.as_view(), name='file-copy-move')
]

urlpatterns = format_suffix_patterns(urlpatterns)