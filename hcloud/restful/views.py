from django.http import Http404
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from django.views.generic import View
from rest_framework.response import Response  
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from hcloud import aws_conf
from . import s3_conn

from .models import File
from .serializers import FileSerializer
from urllib import parse

AWS_UPLOAD_BUCKET = aws_conf.AWS_STORAGE_BUCKET_NAME
AWS_UPLOAD_REGION = aws_conf.AWS_REGION
AWS_UPLOAD_ACCESS_KEY_ID = aws_conf.AWS_ACCESS_KEY_ID
AWS_UPLOAD_SECRET_KEY = aws_conf.AWS_SECRET_ACCESS_KEY
AWS_IDENTITY_POOL = aws_conf.AWS_IDENTITY_POOL

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

    def post(self, request, *args, **kwargs):


        filename_req = request.data.get('filename')
        file_path_req = request.data.get('file_path')
        file_size_req = request.data.get('file_size')
        if not filename_req:
            return Response({"message": "A filename is required"}, status=status.HTTP_400_BAD_REQUEST)

        username_str = str(request.user.username)

        file_obj = File.objects.create(file=file_path_req, size=file_size_req)
        upload_start_path = "{username}/".format(
            username=username_str
        )
        _, file_extension = os.path.splitext(filename_req)
        filename_final = "{file_obj_id}".format(
            file_obj_id=file_path_req
        )

        final_upload_path = "{upload_start_path}{filename_final}".format(
            upload_start_path=upload_start_path,
            filename_final=filename_final,
        )
        if filename_req and file_extension:
            file_obj.path = final_upload_path
            file_obj.save()

        data = {
            "identity_pool": AWS_IDENTITY_POOL,
            "bucket_name": AWS_UPLOAD_BUCKET,
            "bucket_region": AWS_UPLOAD_REGION
        }
        return Response(data, status=status.HTTP_200_OK)


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
        user = request.user
        file = 'media/'+user.username+"/"+path
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


