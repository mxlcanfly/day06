from django.http import JsonResponse
from django.shortcuts import render, redirect
from django import forms
from django.core.validators import ValidationError
from django.urls import reverse
from django.db.models import Q
from django.db import transaction

from utils.encrypt import md5
from web import models
from utils.bookstrap import BootStrapForm
from utils.response import BaseResponse
from utils.pager import Pagination
from utils.group import Option, NbSearchGroup


def customer_list(request):

    search_group = NbSearchGroup(
        request,
        models.Customer,
        Option('level', db_condition={'active':1}),  # choice
    )

    keyword = request.GET.get('keyword', "").strip()
    con = Q()
    if keyword:
        con.connector = "OR"
        con.children.append(('username__contains', keyword))
        con.children.append(('mobile__contains', keyword))
        con.children.append(('level__title__contains', keyword))

    queryset = models.Customer.objects.filter(con).filter(**search_group.get_condition).filter(active=1).select_related('level')
    pager = Pagination(request, queryset)

    context = {
        'queryset':queryset[pager.start: pager.end],
        'paper_string':pager.html(),
        'keyword':keyword,
        'search_group':search_group
    }

    return render(request, 'customer_list.html', context)

class CustomerModelForm(BootStrapForm, forms.ModelForm):
    exculde_style_list = ['level']

    confirm_password = forms.CharField(
        label='重复密码',
        widget=forms.PasswordInput(render_value=True)

    )
    class Meta:
        model = models.Customer
        fields = ['username', 'mobile', 'password', 'confirm_password', 'level']
        widgets = {
            'password':forms.PasswordInput,
            'level':forms.RadioSelect(attrs={'class':'form-radio'})
        }

    def __init__(self,request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['level'].queryset查询到的时level中的所有数据，我们可以对其进行重新赋值，从而实现只显示已激活的数据
        self.fields['level'].queryset = models.Level.objects.filter(active=1)


    def clean_password(self):
        return md5(self.cleaned_data['password'])

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = md5(self.cleaned_data.get('confirm_password'))
        if password != confirm_password:
            raise ValidationError('密码不一致')

        return confirm_password


def customer_add(request):
    if request.method == 'GET':
        form = CustomerModelForm(request)
        return render(request, 'form2.html', {'form':form})

    form = CustomerModelForm(request,data=request.POST)
    if not form.is_valid():
        return render(request, 'form2.html', {'form': form})

    form.instance.creator_id = request.m_user.id
    form.save()
    return redirect(reverse('customer_list'))


class CustomerEditModelForm(BootStrapForm, forms.ModelForm):
    exculde_style_list = ['level']

    class Meta:
        model = models.Customer
        fields = ['username', 'mobile', 'level']
        widgets = {
            'password':forms.PasswordInput,
        }

    def __init__(self,request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['level'].queryset = models.Level.objects.filter(active=1)

def customer_edit(request, pk):
    instance = models.Customer.objects.filter(id=pk).first()
    if request.method == 'GET':
        form = CustomerEditModelForm(request, instance=instance)
        return render(request, 'form2.html', {'form': form})

    form = CustomerEditModelForm(request, data=request.POST, instance=instance)
    if not form.is_valid():
        return render(request, 'form2.html', {'form': form})

    form.save()
    filter_string = request.GET.get('_filter')
    print(filter_string)
    if not filter_string:
        return redirect('/customer/list/')
    return redirect('/customer/list/?{}'.format(filter_string))

class CustomerResetModelForm(BootStrapForm, forms.ModelForm):
    exculde_style_list = ['level']

    confirm_password = forms.CharField(
        label='重复密码',
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Customer
        fields = ['password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput,
        }

    def clean_password(self):
        return md5(self.cleaned_data['password'])

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = md5(self.cleaned_data.get('confirm_password'))
        if password != confirm_password:
            raise ValidationError('密码不一致')

        return confirm_password

def customer_reset(request, pk):
    if request.method == 'GET':
        form = CustomerResetModelForm()
        return render(request, 'form2.html', {'form': form})

    instance = models.Customer.objects.filter(id=pk).first()
    form = CustomerResetModelForm(data=request.POST, instance=instance)
    if not form.is_valid():
        return render(request, 'form2.html', {'form': form})

    form.save()
    return redirect(reverse('customer_list'))

def customer_delete(request):
    cid = request.GET.get('cid', 0)
    if not cid:
        res = BaseResponse(status=False, detail="请选择要删除的数据")
        return JsonResponse(res.dict)

    exists = models.Customer.objects.filter(id=cid, active=1).exists()
    if not exists:
        res = BaseResponse(status=False, detail="要删除的数据不存在")
        return JsonResponse(res.dict)

    res = BaseResponse(status=True)
    models.Customer.objects.filter(id=cid, active=1).update(active=0)
    return JsonResponse(res.dict)

class ChargeModelForm(BootStrapForm, forms.ModelForm):
    charge_type = forms.TypedChoiceField(
        label='类型',
        choices=[(1, "充值"),(2, "扣款")],
        coerce=int
    )
    class Meta:
        model = models.TransactionRecord
        fields = ['charge_type', 'amount']

def customer_charge(request, pk):

    queryset = models.TransactionRecord.objects.filter(customer_id=pk, customer__active=1, active=1).select_related('customer').order_by('-id')
    pager = Pagination(request, query_set=queryset)
    form = ChargeModelForm()

    return render(request, 'customer_charge.html', locals())

def customer_charge_add(request, pk):
    form = ChargeModelForm(data=request.POST)
    if not form.is_valid():
        return JsonResponse({"status":False, "detail":form.errors})

    # 如果校验成功
    amount = form.cleaned_data['amount']
    charge_type = form.cleaned_data['charge_type']
    # 1.对当前操作的客户进行跟新操作，账户余额：增加、减少
    try:
        with transaction.atomic():
            # 加上锁（此处用的是排他锁），以防两个管理员操作的时候出错，事务结束才释放锁
            cus_object = models.Customer.objects.filter(id=pk, active=1).select_for_update().first()

            if charge_type == 2 and cus_object.balance < amount:
                return JsonResponse({"status":False, "detail": {'amount': ['余额不足，账户余额为{}'.format(cus_object.balance)]}})

            if charge_type == 1:
                cus_object.balance = cus_object.balance + amount
            else:
                cus_object.balance = cus_object.balance - amount
            cus_object.save()
            # 2.交易记录
            form.instance.customer = cus_object
            form.instance.creator_id = request.m_user.id
            form.save()
    except Exception as e:
        return JsonResponse({"status":False, "detail":{'amount':['操作失败']}})

    return JsonResponse({"status":True, "detail":form.errors})
