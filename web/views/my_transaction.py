from django.db.models import Q
from django.shortcuts import render
from web import models

from utils.group import Option, NbSearchGroup
from utils.pager import Pagination


def my_transaction_list(request):
    """ 我的交易记录 """
    # 配置展示
    search_group = NbSearchGroup(
        request,
        models.TransactionRecord,
        Option('charge_type'),  # choice
    )

    keyword = request.GET.get('keyword', "").strip()
    con = Q()
    if keyword:
        con.connector = "OR"
        con.children.append(('order_oid__contains', keyword))

    queryset = models.TransactionRecord.objects.filter(con).filter(**search_group.get_condition).filter(
        customer_id=request.m_user.id,
        active=1).order_by('-id')
    pager = Pagination(request, query_set=queryset)
    context = {
        "pager": pager,
        "keyword": keyword,
        "search_group": search_group
    }

    return render(request, "my_transaction_list.html", context)


def transaction_list(request):

    search_group = NbSearchGroup(
        request,
        models.TransactionRecord,
        Option('charge_type'),  # choice
    )

    keyword = request.GET.get('keyword', "").strip()
    con = Q()
    if keyword:
        con.connector = "OR"
        con.children.append(('order_oid__contains', keyword))

    queryset = models.TransactionRecord.objects.filter(con).filter(**search_group.get_condition).filter(
        active=1).order_by('-id')
    pager = Pagination(request, query_set=queryset)
    context = {
        "pager": pager,
        "keyword": keyword,
        "search_group": search_group
    }

    return render(request, 'transaction_list.html', context)