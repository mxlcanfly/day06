import random

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection

from web import models
from utils import tencent

from utils.response import BaseResponse
from web.forms.account import LoginForm,SmsLoginForm,MobileForm

def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request,'login.html',{'form': form})

    #1.接受并获取数据（数据格式是否为空 Form组件 & ModelForm组件）
    form = LoginForm(data=request.POST)
    if not form.is_valid():#自动进行数据的校验
        return render(request,'login.html',{'form': form})

    #2.去数据库校验
    data_dict = form.cleaned_data
    role = data_dict.pop('role')
    print(data_dict,role)

    if role == '1':
        user_object = models.Adminstrator.objects.filter(active=1).filter(**data_dict).first()
    else:
        user_object = models.Customer.objects.filter(active=1).filter(**data_dict).first()


    #2.1 用户或管理员不存在.校验失败
    if not user_object:
        form.add_error('username','用户名或密码错误')
        return render(request, 'login.html', {'form': form})

    #2.2 如果存在（校验成功）就将信息存放到session中
    mapping = {'1':'ADMIN', '2':"CUSTOMER"}
    request.session[settings.M_USERINFO] = {'role':mapping[role], 'name':user_object.username, 'id':user_object.id}
    return redirect(settings.LOGIN_HOME)

def sms_send(request):
    ''' 发送短信 '''
    #1.校验手机号格式
    res = BaseResponse()

    #1.校验数据合法性：手机号 + 角色
    form = MobileForm(data=request.POST)
    if not form.is_valid():
        res.detail = form.errors
        return JsonResponse(res.dict,json_dumps_params={'ensure_ascii':False})#json_dumps_params={'ensure_ascii':False}以中问的形式显示

    #1.5
    mobile = form.cleaned_data['mobile']
    sms_code = str(random.randint(1000, 9999))
    is_success = tencent.send_sms(mobile, sms_code)
    if not is_success:
        res.detail = {'mobile':['发送失败，请稍等重试']}
        return JsonResponse(res.dict, json_dumps_params={'ensure_ascii': False})

    #3.将手机号和雁阵吗保存（以便于下次校验） redis -> 超时时间
    conn = get_redis_connection("default")
    conn.set(mobile, sms_code, ex=60)
    res.status = True

    return JsonResponse(res.dict())

def sms_login(request):
    if request.method == 'GET':
        form = SmsLoginForm()
        return render(request, 'sms_login.html',{'form':form})

    res = BaseResponse()
    #1.手机格式校验
    form = SmsLoginForm(data=request.POST)
    if not form.is_valid():
        res.detail = form.errors
        return JsonResponse(res.dict)

    #2.短信验证码
    role = form.cleaned_data['role']
    mobile = form.cleaned_data['mobile']

    #3.登陆成功 + 注册        （监测手机号是否存在）
    #   - 未注册，自动注册
    #   - 已注册，直接登录
    if role == '1':
        user_object = models.Adminstrator.objects.filter(active=1, mobile=mobile).first()
    else:
        user_object = models.Customer.objects.filter(active=1, mobile=mobile).first()

    if not user_object:
        res.detail = {'mobile':['手机号不存在']}
        return JsonResponse(res.dict)

    mapping = {'1': 'ADMIN', '2': "CUSTOMER"}
    request.session[settings.M_USERINFO] = {'role': mapping[role], 'name': user_object.username, 'id': user_object.id}# 由于这里还要用到mobile在数据可中查询到的值，因此，手机号的校验不易放在钩子函数中了
    res.status = True
    res.data = settings.LOGIN_HOME

    return JsonResponse(res.dict)


def home(request):
    return render(request, 'home.html')


def logout(request):
    request.session.clear()
    return redirect(settings.M_LOGIN)



