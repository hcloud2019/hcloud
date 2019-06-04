from django.http import Http404
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from django.views.generic import View
from rest_framework.response import Response  
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from . import s3_conn

from .models import File
from .serializers import FileSerializer
from urllib import parse

class FileList(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    """
    GET: file list
    """
    def get(self, request, path="/", format=None):
        user = request.user
        data = s3_conn.list_path(s3_conn.BUCKET, user.username, path)
        return Response(data)

    """
    POST : File Upload
    """
    def post(self, request, path="/", format=None):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            data = parse.unquote(file_serializer.data.get('file'))
            file_path = '.' + data
            user = request.user
            data = s3_conn.upload_file(s3_conn.BUCKET, user.username, file_path, path+file_path.split('/')[-1])
            if os.path.exists(file_path):
                os.remove(file_path)

            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    """
    PUT : Make directory
    """
    def put(self, request, path="/", format=None):
        user = request.user
        if path == "public/":
            return Response({'error': 'eeeee'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data = s3_conn.make_directory(s3_conn.BUCKET, user.username, path)
            return Response(data, status=status.HTTP_201_CREATED)

class FileDetail(APIView):

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, path="/", format=None):
        file = 'media/'+path
        user = request.user
        s3_conn.download_file(s3_conn.BUCKET, user.username, file, path)
        return Response({'file': file})

    def delete(self, request, path="/", format=None):
        user = request.user
        result = s3_conn.delete_path(s3_conn.BUCKET, user.username, path)
        return Response(result)


class FileCopyMove(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, old_path, new_path, format=None):
        user = request.user
        if request.data.get('method') == 'move':
            s3_conn.move_file(s3_conn.BUCKET, user.username, old_path, new_path)
        elif request.data.get('method') == 'copy':
            s3_conn.copy_file(s3_conn.BUCKET, user.username, old_path, new_path)
        else:
            return Response({'stats': 'bad_request'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'old_path': old_path, 'new_path': new_path})


