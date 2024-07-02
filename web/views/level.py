from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse

from web import models
from utils.bookstrap import BootStrapForm


class LevelModelForm(BootStrapForm, forms.ModelForm): # 适合数据库的增删改查
    class Meta:
        model = models.Level# lable就是创建数据库时的verbose_name
        fields = ['title', 'precent']


def level_list(request):
    queryset = models.Level.objects.filter(active=1)
    return render(request, 'level_list.html', {'queryset': queryset})

def level_add(request):
    if request.method == 'GET':
        form = LevelModelForm()
        return render(request, 'form.html', {'form': form})
    form = LevelModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'form.html', {'form': form})

    form.save()

    return redirect(reverse('level_list'))

def level_edit(request, pk):
    level_object = models.Level.objects.filter(id=pk).first()
    if request.method == 'GET':
        form = LevelModelForm(instance=level_object)
        return render(request, 'form.html', {'form':form})

    form = LevelModelForm(data=request.POST, instance=level_object)
    if not form.is_valid():
        return render(request, 'form.html', {'form':form})

    form.save()
    return redirect(reverse('level_list'))

def level_delete(request, pk):

    exist = models.Customer.objects.filter(level_id=pk).exists()
    if not exist:
        models.Level.objects.filter(id=pk).update(active=0)
    return redirect(reverse('level_list'))
