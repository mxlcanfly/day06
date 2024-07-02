"""
如果想要以后使用分页，需要两个步骤
在视图函数中：
V1版本：
    def customer_list(request):
        queryset = models.Customer.objects.filter(active=1).select_related('level')

        pager = Pagination(request, queryset)
        context = {
            'queryset':queryset[pager.start: pager.end],
            'paper_string':pager.html()
        }
        return render(request, 'customer_list.html', context)

    在页面上：
        {% for row in queryset %}
            {{ row.id }}
        {% endfor %}

        <ul class="pagination">
            {{ paper_string }}
        </ul>

V2版本：
    def customer_list(request):
        queryset = models.Customer.objects.filter(active=1).select_related('level')

        pager = Pagination(request, queryset)
        return render(request, 'customer_list.html', context， {'pager':pager})

    在页面上：
        {% for row in pager.queryset %}
            {{ row.id }}
        {% endfor %}

        <ul class="pagination">
            {{ pager.html }}
        </ul>
"""
import copy
from django.utils.safestring import mark_safe

class Pagination(object):
    def __init__(self, request, query_set, pre_page_count=10):
        self.query_dict = copy.deepcopy(request.GET)
        self.query_dict._matable = True

        self.query_set = query_set
        self.total_count = query_set.count()
        self.total_page, div = divmod(self.total_count, pre_page_count)
        if div:
            self.total_page += 1

        page = request.GET.get('page')
        if not page:
            page = 1
        else:
            if not page.isdecimal():
                page = 1
            else:
                page = int(page)# 用户可能写的是字符串
                if page <= 0:
                    page = 1
                else:
                    if page > self.total_page:
                        page = self.total_page

        self.page = page
        self.pre_page_count = pre_page_count

        self.start = (page - 1) * pre_page_count
        self.end = page * pre_page_count

    def html(self):
        paper_list = []

        if self.total_page <= 11:
            start_page = 1
            end_page = self.total_page
        else:
            if self.page <= 6:
                start_page = 1
                end_page = 11
            else:
                if (self.page + 5) > self.total_page:
                    start_page = self.total_page - 10
                    end_page = self.total_page
                else:
                    start_page = self.page - 5
                    end_page = self.page + 5

        self.query_dict.setlist('page',[1])
        paper_list.append('<li><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode()))

        if self.page > 1:
            self.query_dict.setlist('page',[self.page - 1])
            paper_list.append('<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode()))

        for i in range(start_page, end_page + 1):
            self.query_dict.setlist('page',[i])
            if i == self.page:
                item = '<li class="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                item = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            paper_list.append(item)


        if self.page < self.total_page:
            self.query_dict.setlist('page',[self.page + 1])
            paper_list.append('<li><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode()))

        self.query_dict.setlist('page',[self.total_page])
        paper_list.append('<li><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode()))

        paper_list.append('<li class="disabled"><a>数据共{}条{}页</a></li>'.format(self.total_count, self.total_page))
        paper_string = mark_safe(''.join(paper_list))
        return paper_string

    def queryset(self):
        return self.query_set[self.start:self.end]