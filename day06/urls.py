"""day06 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web.views import account, level, customer, policy, my_order, my_transaction

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/', account.login,name='login'),
    path('sms/login/', account.sms_login,name='sms_login'),
    path('sms/send/', account.sms_send,name='sms_send'),
    path('home/', account.home,name='home'),
    path('logout/', account.logout, name='logout'),

    path('level/list/', level.level_list,name='level_list'),
    path('level/add/', level.level_add,name='level_add'),
    path('level/edit/<int:pk>/', level.level_edit,name='level_edit'),
    path('level/delete/<int:pk>/', level.level_delete,name='level_delete'),

    path('customer/list/', customer.customer_list,name='customer_list'),
    path('customer/add/', customer.customer_add,name='customer_add'),
    path('customer/edit/<int:pk>/', customer.customer_edit,name='customer_edit'),
    path('customer/reset/<int:pk>/', customer.customer_reset,name='customer_reset'),
    path('customer/delete/', customer.customer_delete,name='customer_delete'),
    path('customer/charge/<int:pk>/', customer.customer_charge,name='customer_charge'),
    path('customer/charge/<int:pk>/add', customer.customer_charge_add,name='customer_charge_add'),

    path('policy/list/', policy.policy_list, name='policy_list'),
    path('policy/add/', policy.policy_add, name='policy_add'),
    path('policy/edit/<int:pk>/', policy.policy_edit, name='policy_edit'),
    path('policy/delete/', policy.policy_delete, name='policy_delete'),


    path('my/order/list/', my_order.my_order_list, name='my_order_list'),
    path('my/order/add/', my_order.my_order_add, name='my_order_add'),
    path('my/order/cancel/<int:pk>/', my_order.my_order_cancel, name='my_order_cancel'),

    path('my/transaction/list/', my_transaction.my_transaction_list, name='my_transaction_list'),
    path('transaction/list/', my_transaction.transaction_list, name='transaction_list'),

]
