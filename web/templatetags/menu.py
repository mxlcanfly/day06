from copy import deepcopy

from django.template import Library
from django.conf import settings


register = Library()

@register.inclusion_tag('tag/m_menu.html')
def m_menu(request):

    user_menu_list = deepcopy(settings.M_MENU[request.m_user.role])# 为了放置每次读取全局的setting，因为每次匹配成功都会在对应的标签上加入class=active标签，因此，要进行deepcopy操作
    for item in user_menu_list:
        for child in item['children']:
            # if child['url'] == request.path_info:
            if child['name'] == request.m_user.menu_name:
                child['class'] = 'active'

    return {'menu_list'
            :user_menu_list}
