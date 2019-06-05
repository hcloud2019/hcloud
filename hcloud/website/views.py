from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from restful.models import File
from django.views import View
from django.core.files.base import ContentFile
from django.middleware import csrf
from hcloud import settings
from django.http import HttpResponse
from django.contrib import messages

import os
import requests
import json
import urllib
import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hcloud', user='postgres', password='', port='5432')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def home(request):
    return render(request, 'Website/home.html')

@login_required
def filelist(request, path):
    cookies = {'sessionid': request.session.session_key}
    files = requests.get(
        'http://localhost:8000/restapi/list/' + path, cookies=cookies)
    ret = files.json()  # dictionary
    ret['path'] = path

    folder_ret = [x for x in ret['files'] if x['type'] == 'directory']
    file_ret = [x for x in ret['files'] if x['type'] == 'file']

    # url의 쿼리스트링을 가져온다. 없는 경우 공백을 리턴한다
    sort = request.GET.get('sort', '')

    ret = files.json()
    ret['path'] = path

    sort = request.GET.get('sort', '')  # url의 쿼리스트링을 가져온다. 없는 경우 공백을 리턴한다

    if sort == 'date-end':  # 과거순
        return render(request, 'Website/filelist.html',
                      {'files': folder_ret + sorted(file_ret, key=lambda k: k['time'])})
    elif sort == 'name':  # 이름순
        return render(request, 'Website/filelist.html',
                      {'files': folder_ret + sorted(file_ret, key=lambda k: k['name'])})
    elif sort == 'date':  # 최신순
        return render(request, 'Website/filelist.html',
                      {'files': folder_ret + sorted(file_ret, key=lambda k: k['time'], reverse=True)})
    else:
        return render(request, 'Website/filelist.html', ret)


@login_required
def upload(request, path):
    file = request.FILES.get('file')
    cookie = {'sessionid': request.session.session_key}
    cookie['csrftoken'] = csrf.get_token(request)
    header = {'X-CSRFToken': cookie['csrftoken']}
    requests.post('http://localhost:8000/restapi/list/' + path,
                  files={'file': file}, headers=header, cookies=cookie)
                  
    return redirect('filelist', path=path)


@login_required
def makefolder(request, path):
    dir_name = request.POST.get('dir_name')
    cookie = {'sessionid': request.session.session_key}
    cookie['csrftoken'] = csrf.get_token(request)
    header = {'X-CSRFToken': cookie['csrftoken']}
    print("dir_name : ", dir_name)
    files = requests.put(
        'http://localhost:8000/restapi/list/' + path, headers=header, cookies=cookie)
    files.raise_for_status()
    return redirect('filelist', path=path)


@login_required
def delete(request, path):
    cookie = {'sessionid': request.session.session_key}
    cookie['csrftoken'] = csrf.get_token(request)
    header = {'X-CSRFToken': cookie['csrftoken']}
    requests.delete('http://localhost:8000/restapi/file/' +
                    path, headers=header, cookies=cookie)
    new_path = "/".join(path.split("/")[:-1])
    if new_path != '':
        new_path = new_path + '/'
    return redirect('filelist', path=new_path)


@login_required
def download(request, path):
    cookie = {'sessionid': request.session.session_key}
    requests.get('http://localhost:8000/restapi/file/' + path, cookies=cookie)
    user = request.user
    local_path = os.path.join(settings.MEDIA_ROOT, user.username+"/"+path)
    if os.path.exists(local_path):
        with open(local_path, 'rb') as down_file:
            response = HttpResponse(
                down_file.read(), content_type='multipart/form-data')
            response['Content-Disposition'] = 'inline; filename=' + \
                                              os.path.basename(local_path)
            return response
    raise Http404


@login_required
def view(request, path):
    cookie = {'sessionid': request.session.session_key}
    requests.get('http://localhost:8000/restapi/file/' + path, cookies=cookie)
    user = request.user
    local_path = os.path.join(settings.MEDIA_ROOT, user.username+"/"+path)
    
    if os.path.exists(local_path):
        with open(local_path, 'rb') as down_file:
            response = HttpResponse(down_file.read(), content_type='text/plain')
            response['Content-Disposition'] = 'inline; filename=' + \
                                              os.path.basename(local_path)
            return response
    raise Http404


@login_required
def copy(request, old_path, new_path):
    cookie = {'sessionid': request.session.session_key}
    cookie['csrftoken'] = csrf.get_token(request)
    header = {'X-CSRFToken': cookie['csrftoken']}
    files = requests.post('http://localhost:8000/restapi/file-mod/' + old_path + '&' + new_path, data={'method': 'copy'},
                          headers=header, cookies=cookie)

    new_path = "/".join(new_path.split("/")[:-1])
    if new_path != '':
        new_path = new_path + '/'
    return redirect('filelist', path=new_path)


@login_required
def move(request, old_path, new_path):
    cookie = {'sessionid': request.session.session_key}
    cookie['csrftoken'] = csrf.get_token(request)
    header = {'X-CSRFToken': cookie['csrftoken']}
    files = requests.post('http://localhost:8000/restapi/file-mod/' + old_path + '&' + new_path, data={'method': 'move'},
                          headers=header, cookies=cookie)

    new_path = "/".join(new_path.split("/")[:-1])
    if new_path != '':
        new_path = new_path + '/'
    return redirect('filelist', path=new_path)

@login_required
def search(request, file_name):
    file_name = file_name[0:len(file_name)-1]
    #connect db
    try:
        cur = conn.cursor()
    except:
        print("Connection Error")
    #select query
    try:
        temp = "'%" + file_name+"'"
        sql = "select file_name from public.file_name where file_name LIKE %s " % (temp)
        cur.execute(sql)
        search=[]
        data = cur.fetchall()
        files = []
        for i in data :
            temp_item=""
            temp = i[0].split('/')
            if temp[0] =="public" :
                search.append(i[0])
            else :
                for j in range(1,len(temp)) : 
                    if j == len(temp)-1:
                        temp_item += temp[j]
                    else :
                        temp_item += (temp[j]+'/')

                search.append(temp_item)

        for item in search:
            if(file_name==item.split('/')[-1]):
                files.append(item)
        
    except:
        conn.rollback()
    #완전 일치하는 파일이 없는 경우
    if (len(files)==0):
        return redirect('filelist', path="")
    
    dic_files = {"files" : []}
    for file in files :
        dic_files["files"].append(file)

    dic_files["name"] = file_name
    return render(request, 'Website/search.html', dic_files)
