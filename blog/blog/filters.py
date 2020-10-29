from django_filters import rest_framework as drf_filters

from .models import Post


class PostFilter(drf_filters.FilterSet):
    """
    当用户传递 created_year 查询参数时，django-filter 实际上会将以上定义的规则翻译为如下的 ORM 查询语句：
    Post.objects.filter(created_time__year=created_year传递的值)
    """
    # 查询参数名 = 查询参数值的类型（查询的模型字段，查询表达式）
    created_year = drf_filters.NumberFilter(
        field_name="created_time", lookup_expr="year", help_text="根据文章发表年份过滤文章列表。"
    )
    created_month = drf_filters.NumberFilter(
        field_name="created_time", lookup_expr="month", help_text="根据文章发表月份过滤文章列表。"
    )

    class Meta:
        model = Post
        # category，tags 两个过滤字段因为是 Post 模型中定义的字段，因此 django-filter 可以自动推断其过滤规则
        fields = ["category", "tags", "created_year", "created_month"]
