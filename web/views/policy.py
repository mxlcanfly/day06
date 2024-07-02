from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q

from web import models
from utils.pager import Pagination
from utils.bookstrap import BootStrapForm
from utils.response import BaseResponse

def policy_list(request):
    from django.core.handlers.wsgi import WSGIRequest

    keyword = request.GET.get('keyword', "").strip()
    con = Q()
    if keyword:
        con.children.append(("count__contains", keyword))

    queryset = models.PricePolicy.objects.filter(con).all().order_by('count')
    pager = Pagination(request, queryset)

    return render(request, 'policy_list.html', {'pager':pager})

class PolicyAddModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.PricePolicy
        fields = '__all__'


def policy_add(request):
    if request.method == "GET":
        form = PolicyAddModelForm()
        return render(request, 'form4.html', {"form":form})

    form = PolicyAddModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'form4.html', {"form":form})

    form.save()
    return redirect(reverse('policy_list'))

def policy_edit(request, pk):
    instance = models.PricePolicy.objects.filter(id=pk).first()
    if request.method == "GET":
        form = PolicyAddModelForm(instance=instance)
        return render(request, 'form4.html', {"form":form})

    form = PolicyAddModelForm(data=request.POST ,instance=instance)
    if not form.is_valid():
        return render(request, 'form4.html', {"form": form})

    form.save()
    return redirect(reverse('policy_list'))

def policy_delete(request):
    res = BaseResponse(status=True)
    cid = request.GET.get("cid")
    models.PricePolicy.objects.filter(id=cid).delete()
    return JsonResponse(res.dict)
