from django import forms
from django_redis import get_redis_connection

from utils.encrypt import md5
from django.core.validators import RegexValidator,ValidationError

from web import models


class LoginForm(forms.Form):
    role = forms.ChoiceField(
        label='角色',
        choices=(('1','管理员'), ('2','用户')),
        widget=forms.Select(attrs={'class':'form-control'})
    )
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':"用户名"})
    )
    password = forms.CharField(
        label='密码',
        # min_length=6,
        # max_length=10,
        # validators=[RegexValidator(r'^[0-9]+$','密码必须是数字')],
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':"密码"})#默认在返回页面时，不保留密码，如果想要保留密码，需要设置render_value=True
    )

    def clean_username(self):
        user = self.cleaned_data['username']
        if len(user) < 3:
            from django.core.exceptions import ValidationError
            raise ValidationError("用户名格式错误")
        return user

    def clean_password(self):
        return md5(self.cleaned_data['password'])

    def clean(self):
        pass

    def _post_clean(self):
        pass

class Level_Add_Form(forms.Form):
    level = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    precent = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


class SmsLoginForm(forms.Form):
    role = forms.ChoiceField(
        label='角色',
        choices=(('1', '管理员'), ('2', '用户')),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    mobile = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1[358]\d{9}$', '手机格式错误')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "手机号"})
    )
    code = forms.CharField(
        label='短信验证码',
        validators=[RegexValidator(r'^[0-9]{4}$', '验证码格式错误')],
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "短信验证码"})
        # 默认在返回页面时，不保留密码，如果想要保留密码，需要设置render_value=True
    )

    def clean_code(self):
        mobile = self.cleaned_data.get('mobile')
        code = self.cleaned_data['code']
        if not mobile:
            return code # 如果mobile校验没通过，获取不到它的值，那么就直接返回该字段，约等于什么也不做

        conn = get_redis_connection('default')
        cache_code = conn.get(mobile)
        if not cache_code:
            return ValidationError('短信验证码未发送或失效')

        if code != cache_code.decode('utf-8'):
            return ValidationError('短信验证错误')

class MobileForm(forms.Form):
    role = forms.ChoiceField(
        label='角色',
        choices=(('1', '管理员'), ('2', '用户')),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    mobile = forms.CharField(
        label='手机号',
        required=True,
        validators=[RegexValidator(r'^1[358]\d{9}$', '手机号格式错误')]
    )

    def clean_mobile(self):
        #从上到下运行，如果role存在，则可以获取role，否则获取不到
        role = self.cleaned_data.get('role')
        mobile = self.cleaned_data['mobile']
        if not role:
            return mobile

        if role == '1':
            exist = models.Adminstrator.objects.filter(active=1, mobile=mobile).exists()
        else:
            exist = models.Customer.objects.filter(active=1, mobile=mobile).exists()

        if not exist:
           return ValidationError('手机号不存在')

        return mobile

