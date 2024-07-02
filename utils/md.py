from django.shortcuts import redirect, render
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse

class UserInfo(object):
    def __init__(self, id , name, role):
        self.id = id
        self.name = name
        self.role = role
        self.menu_name = None
        self.text_lsit = []

class AuthMiddleWare(MiddlewareMixin):

    def is_white_url(self,request):
        if request.path_info in settings.M_DIRECT_VISIT:
            return True

    def process_request(self, request):
        ''' 校验用户是否已登陆'''
        # 1.不需要登录进可以访问的url（由于中间件先运行，如果不将可以直接访问的url先处理，可能导致重定向错误的问题）
        if self.is_white_url(request):
            return

        #2.session中获取用户信息，能获取到登陆成功；否者未登录返回登陆界面
        user_dict = request.session.get(settings.M_USERINFO)

        #3.未登录，跳转回登陆界面
        if not user_dict:
            return redirect(settings.M_LOGIN)

        #4.已登录，封装用户信息，以便于后面取
        request.m_user = UserInfo(**user_dict)

    def process_view(self, request, callback, callback_args, callback_kwargs):

        if self.is_white_url(request):# 'WSGIRequest' object has no attribute 'm_user'这个问题是由于前面的process_request中遇到白名单就直接向后运行了，因此request中还没有m_user
            return                    # 只需要在process_view 中也让白名单直接通过即可

        # 1.获取当前用户所访问的url
        current_name = request.resolver_match.url_name

        if current_name in settings.M_PREMISSION_PUBLIC:
            return

        #2.获取当前用户所拥有的权限
        user_premission_dict = settings.M_PREMISSION[request.m_user.role]

        #3.判断是否拥有该权限
        if current_name not in user_premission_dict:

            if request.is_ajax():
                return JsonResponse({'status':False, 'detail':'无权访问'})
            return render(request, 'premission.html')

        #4.有权限
        menu_name = current_name

        text_list = []
        text_list.append(user_premission_dict[menu_name]['text'])

        while user_premission_dict[menu_name]['parent']:
            menu_name = user_premission_dict[menu_name]['parent']
            text_list.append(user_premission_dict[menu_name]['text'])

        text_list.append('首页')
        text_list.reverse()
        request.m_user.text_list = text_list

        #4.1当前菜单的值
        request.m_user.menu_name = menu_name


