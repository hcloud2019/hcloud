import boto3
import os
import json
import datetime
from hcloud import aws_conf
import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hcloud', user='', password='', port='5432')

BUCKET = aws_conf.AWS_STORAGE_BUCKET_NAME

S3Bucket = boto3.Session(
    aws_access_key_id=aws_conf.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_conf.AWS_SECRET_ACCESS_KEY
).resource('s3').Bucket(BUCKET)

S3 = boto3.client(
    's3',
    aws_access_key_id=aws_conf.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_conf.AWS_SECRET_ACCESS_KEY)



def list_path(bucket, user, path):
    files = []
    prefix = '{}/{}'.format(user, path)

    # if given path is public path
    if path.startswith('public'):
        prefix = '{}'.format(path)

    # get list
    objects = S3.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')

    # get sub directories
    common_prefixes = objects.get('CommonPrefixes')


    if common_prefixes:
        for obj in common_prefixes:
            files.append({'type': 'directory', 'name': obj.get('Prefix').split('/')[-2]})  # 최상위 subdir

    # get files
    contents = objects.get('Contents')
    if contents:
        for obj in contents:
            file = obj.get('Key').split('/')[-1]
            if file != '':
                files.append({'type': 'file', 'name': file, 'time': obj.get("LastModified")})

    # add public directory if path is root directory'
    if path == '':
        files.append({'type': 'directory', 'name': 'public','time': '2019-05-01 00:00:54+00:00'})

    return {'files': files}


def upload_file(bucket, user, local_path, key):
    print(bucket, user, local_path, key)
    # test-bucket-hcloud    hyuna    ./media/4_sk.png    4_sk.png
    # ./media/5b.png    p2/5b.png

    # public prefix
    if (key.startswith("public")):
        prefix = key
    # private prefix
    else:
        prefix = user + "/" + key
    try:
        cur = conn.cursor()
    except:
        print("Connection Error")
    try:
        temp = "'" + prefix + "'"
        sql = "Insert Into public.file_name (file_name) VALUES (%s)" % (temp)
        print(sql)
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()
        print("ERROR : db insert")

    path = '{}/{}'.format(user, key)
    if key.startswith('public'):
        path = '{}'.format(key)

    return S3.upload_file(local_path, bucket, path)


def download_file(bucket, user, local_path, key):
    temp = local_path.split('/')
    tmp_dir=""
    for i in range(1,len(temp)-1):
        tmp_dir += ('/'+temp[i])

    base = os.path.abspath("media")
    if not os.path.isdir(base+tmp_dir):
        os.makedirs(base+tmp_dir)
    
    #public view / download
    if key.split('/')[0]=="public":
        public_dir =""
        for i in range(1,len(temp)-1):
            public_dir += ('/'+temp[i])
        if not os.path.isdir(base+public_dir):
                os.makedirs(base+public_dir)
        return S3.download_file(bucket, key, local_path)

    return S3.download_file(bucket, user + "/" + key, local_path)


def delete_path(bucket, user, path):
    prefix = "{}/{}".format(user, path)
    if path.startswith('public'):
        prefix = '{}'.format(path)
    # print(user, path, prefix)
    S3Bucket.objects.filter(Prefix=prefix).delete()

    try:
        cur = conn.cursor()
    except:
        print("Connection Error")

    try:
        temp = "'%" + path + "%'"
        sql = "select file_name from public.file_name where file_name LIKE %s " % (temp)
        print(sql)
        cur.execute(sql)
        data = cur.fetchall()
        temp2 = "'" + data[0][0] + "'"
        sql = "delete from public.file_name where file_name = %s" % (temp2)
        print(sql)
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()
        print("ERROR : db delete")


def make_directory(bucket, user, path):
    key = '{}/{}'.format(user, path)
    if path.split('/')[0] + '/' == path == 'public/':  # 최상위 디렉토리에서 폴더 생성
        key = ''
    else:
        if path.startswith('public'):
            key = '{}'.format(path)
        return S3.put_object(Bucket=BUCKET, Key=key)


def move_file(bucket, user, old_path, new_path):
    copysource = bucket + "/" + user + "/" + old_path
    del_key = user + "/" + old_path
    key = user + "/" + new_path
    if old_path.split('/')[0]=="public":
        copysource = bucket + "/" + old_path
        del_key = old_path
    if new_path.split('/')[0]=="public":
        key=new_path

    S3.copy_object(Bucket=bucket, CopySource=copysource, Key=key)
    return S3.delete_object(Bucket=bucket, Key=del_key)
    


def copy_file(bucket, user, old_path, new_path):
    copysource = bucket + "/" + user + "/" + old_path
    key = user + "/" + new_path
    if old_path.split('/')[0]=="public":
        copysource = bucket + "/" + old_path
    if new_path.split('/')[0]=="public":
        key=new_path

    return S3.copy_object(Bucket=bucket, CopySource=copysource, Key=key)
    
