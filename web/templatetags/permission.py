from django.http import QueryDict
from django.template import Library
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

register = Library()

def check_permission(request, name):
    # 1.获取当前用户角色
    role = request.m_user.role
    # 2.根据角色获取他所有的权限字典
    permission_dict = settings.M_PREMISSION[role]
    # 3.判断它是否具有权限
    if name in permission_dict:
        return True

    if name in settings.M_PREMISSION_PUBLIC:
        return True

@register.simple_tag
def add_permission(request, name, *args, **kwargs):

    if not check_permission(request, name):
        return ""
    # 无权限，返回空
    url = reverse(name, args=args, kwargs=kwargs)
    # 有权限，返回
    tpl = """
    <a class='btn btn-success' href="{}" >
        <span class='glyphicon glyphicon-plus-sign'></span> 新建
    </a>
    """.format(url)
    return mark_safe(tpl)

@register.simple_tag
def edit_permission(request, name, *args, **kwargs):

    if not check_permission(request, name):
        return ""
    # 无权限，返回空
    url = reverse(name, args=args, kwargs=kwargs)

    if request.GET.urlencode():
        param = request.GET.urlencode()
        new_query_dict = QueryDict(mutable=True)
        new_query_dict['_filter'] = param
        param_string = new_query_dict.urlencode()
        # 有权限，返回
        tpl = """<a href="{}?{}" class="btn btn-primary btn-xs">编辑</a>""".format(url, param_string)
        return mark_safe(tpl)
    else:
        tpl = """<a href="{}" class="btn btn-primary btn-xs">编辑</a>""".format(url)
        return mark_safe(tpl)

@register.simple_tag
def delete_permission(request, name, *args, **kwargs):

    if not check_permission(request, name):
        return ""
    # 无权限，返回空
    pk = kwargs.get('pk')
    # 有权限，返回
    tpl = """
    <a cid={} class="btn btn-danger btn-xs btn-delete">删除</a>
    """.format(pk)
    return mark_safe(tpl)

@register.simple_tag
def delete_url_permission(request, name, *args, **kwargs):

    if not check_permission(request, name):
        return ""
    # 无权限，返回空
    pk = kwargs.get('pk')
    url = reverse(name, args=args, kwargs=kwargs)
    # 有权限，返回
    tpl = """
    <a href="{}" class="btn btn-danger btn-xs btn-delete">删除</a>
    """.format(url)
    return mark_safe(tpl)

@register.filter
def has_permission(request, others):
    name_list = others.split(',')
    for name in name_list:
        status = check_permission(request,name)
        if status:
            return True
    return False