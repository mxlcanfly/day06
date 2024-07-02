import datetime
import random

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models import F
from django import forms
from django_redis import get_redis_connection
from django.conf import settings
from django.db import transaction

from web import models
from utils.video import get_old_view_count
from utils.pager import Pagination
from utils.bookstrap import BootStrapForm


def my_order_list(request):
    queryset = models.Order.objects.filter(customer_id=request.m_user.id, active=1).order_by('-id')
    pager = Pagination(request, query_set=queryset)
    return render(request, 'my_order_list.html', {'pager':pager})


class MyOrderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model=models.Order
        fields = ['url', 'count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        price_count_list = []
        text_count_list = []
        queryset = models.PricePolicy.objects.all().order_by('count')
        for item in queryset:
            unit_price = item.price / item.count
            price_count_list.append([item.count, ">={} ￥{}/条".format(item.count, unit_price), unit_price])
            text_count_list.append(">={} ￥{}/条".format(item.count, unit_price))
        if text_count_list:
            self.fields['count'].help_text = '.'.join(text_count_list)
        else:
            self.fields['count'].help_text = '请联系管理员设置价格'
        self.price_count_list = price_count_list


    def clean_count(self):
        count = self.cleaned_data['count']
        if not self.price_count_list:
            raise ValidationError("请联系管理员设置价格")

        min_count_limit = self.price_count_list[0][0]

        if count < min_count_limit:
            raise ValidationError("最低支持数量为：{}".format(min_count_limit))
        return count

def my_order_add(request):
    if request.method == 'GET':
        form = MyOrderModelForm()
        return render(request, 'form.html', {'form':form})

    form = MyOrderModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'form.html', {'form': form})

    print(form.cleaned_data)

    video_url = form.cleaned_data['url']
    count = form.cleaned_data['count']
    print(video_url, count)

    # 0.
    status, old_view_count = get_old_view_count(video_url)
    print(video_url, status, old_view_count)
    if not status:
        form.add_error('url', '视频原来播放获取失败')
        return render(request, 'form.html', {'form': form})

    # 1.根据数量获取单价，计算出原价
    for idx in range(len(form.price_count_list) -1, -1, -1):
        limit_count, _, unit_price = form.price_count_list[idx]
        if count >= limit_count:
            break
    total_price = count * unit_price
    print(total_price)

    # 2.根据客户的级别，根据级别计算出折扣后的价格
    try:
        with transaction.atomic():
            cus_object = models.Customer.objects.filter(id=request.m_user.id).select_for_update().first()
            real_price = total_price * cus_object.level.precent / 100
            print(real_price, type(real_price))

            # 3.判断账户余额够不够
            print(cus_object.balance, type(cus_object.balance))
            if cus_object.balance < real_price:
                form.add_error('count', '账户余额不足')
                return render(request, 'form.html', {'form': form})

            # 4.创建订单
            # 4.1 生成订单号
            while True:
                rend_number = random.randint(10000000, 99999999)
                print(rend_number)
                ctime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                print(ctime)
                oid = "{}{}".format(ctime, rend_number)
                exists = models.Order.objects.filter(oid=oid).exists()
                if exists:
                    continue
                break
            print(oid)
            # 4.2 爬虫，发送网络请求获取原播放
            print('原播放', old_view_count)

            form.instance.oid = oid
            form.instance.price = total_price
            form.instance.real_price = real_price
            form.instance.old_view_count = old_view_count
            form.instance.customer_id = request.m_user.id
            form.save()

            # 5.客户扣款
            models.Customer.objects.filter(id=request.m_user.id).update(balance=F('balance') - real_price)
            # cus_object.balance = cus_object.balance -real_price
            # cus_object.save()

            # 6.生成交易记录
            models.TransactionRecord.objects.create(
                charge_type=3,
                customer_id=request.m_user.id,
                amount=real_price,
                order_oid=oid
            )

            # 7.写入队列redis(redis启动，django连接redis)
            conn = get_redis_connection("default")
            conn.lpush(settings.QUEUE_TASK_NAME, oid)
    except Exception as e:
        form.add_error('count','创建订单失败')
        return render(request, 'form.html', {'form': form})

    return redirect('/my/order/list/')

def my_order_cancel(request, pk):
    ''' 撤单 '''
    order_object = models.Order.objects.filter(pk=pk, active=1, status=1, customer=request.m_user.id).first()
    if not order_object:
        messages.add_message(request, settings.MESSAGE_DANGER_TAG, '订单不存在')
        return redirect('/my/order/list/')

    try:
        with transaction.atomic():
            cus_object = models.Customer.objects.filter(id=request.m_user.id).select_for_update().first()

            # 1.订单状态变化
            models.Order.objects.filter(pk=pk, active=1, status=1, customer=request.m_user.id).update(status=5)

            # 2.归还余额
            models.Customer.objects.filter(id=request.m_user.id).update(balance=F('balance') + order_object.real_price)

            # 3.交易记录
            models.TransactionRecord.objects.create(
                charge_type=5,
                customer_id=request.m_user.id,
                amount=order_object.real_price,
                order_oid=order_object.oid
            )
            # 撤单成功了
            messages.add_message(request, messages.SUCCESS, "撤单成功")
            return redirect('/my/order/list/')

    except Exception as e:
        messages.add_message(request, settings.MESSAGE_DANGER_TAG, '扯淡失败，{}'.format(str(e)))
        return redirect('/my/order/list/')



