import re

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from pure_pagination.mixins import PaginationMixin
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import DateField
# from rest_framework_extensions.cache.decorators import cache_response
# from rest_framework_extensions.key_constructor.bits import ListSqlQueryKeyBit, PaginationKeyBit, RetrieveSqlQueryKeyBit
# from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor

from comments.serializers import CommentSerializer
from .filters import PostFilter
from .models import Post, Category, Tag


# 替换成 IndexView 类视图
# def index(request):
#     post_list = Post.objects.all()
#     return render(request, 'blog/index.html', context={
#         'post_list': post_list,
#     })
from .serializers import PostListSerializer, PostRetrieveSerializer, TagSerializer, CategorySerializer
# from .utils import UpdatedAtKeyBit


class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 10


# 替换成 CategoryView 类视图
# def category(request, pk):
#     cate = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class CategoryView(IndexView):
    def get_queryset(self):
        """
        该方法默认获取指定模型的全部列表数据，复写他修改默认行为
        """
        cate = get_object_or_404(Category, pk=self.kwargs.get("pk"))
        return super().get_queryset().filter(category=cate)


# 替换成 TagView 类视图
# def tag(request, pk):
#     t = get_object_or_404(Tag, pk=pk)
#     post_list = Post.objects.filter(tags=t)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class TagView(IndexView):
    def get_queryset(self):
        t = get_object_or_404(Tag, pk=self.kwargs.get("pk"))
        return super().get_queryset().filter(tags=t)


# 替换成 ArchiveView 类视图
# def archive(request, year, month):
#     post_list = Post.objects.filter(created_time__year=year, created_time__month=month)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class ArchiveView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get("year")
        month = self.kwargs.get("month")
        return (
            super()
            .get_queryset()
            .filter(created_time__year=year, created_time__month=month)
        )

# 替换成 PostDetailView 类视图
# def detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#
#     # 阅读量 +1
#     post.increase_views()
#
#     md = markdown.Markdown(extensions=[
#         'markdown.extensions.extra',
#         'markdown.extensions.codehilite',
#         TocExtension(slugify=slugify),
#     ])
#     post.body = md.convert(post.body)
#
#     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
#     post.toc = m.group(1) if m is not None else ''
#
#     return render(request, 'blog/detail.html', context={'post': post})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        """
        可以简单地把 get 方法的调用看成是 detail 视图函数的调用
        """
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response


def search(request):
    q = request.GET.get('q')

    if not q:
        error_msg = "请输入搜索关键词"
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    # title 中包含（contains）关键字 q，前缀 i 表示不区分大小写
    # Q 对象用于包装查询表达式，其作用是为了提供复杂的查询逻辑
    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'post_list': post_list})


# ---------------------------------------------------------------------------
#   Django REST framework 接口
# ---------------------------------------------------------------------------


# class PostUpdatedAtKeyBit(UpdatedAtKeyBit):
#     key = "post_updated_at"
#
#
# class CommentUpdatedAtKeyBit(UpdatedAtKeyBit):
#     key = "comment_updated_at"
#
#
# class PostListKeyConstructor(DefaultKeyConstructor):
#     list_sql = ListSqlQueryKeyBit()  # 缓存 key bit: 执行数据库查询的 sql 查询语句
#     pagination = PaginationKeyBit()  # 分页请求的查询参数
#     updated_at = PostUpdatedAtKeyBit()  # Post 资源的最新更新时间
#
#
# class PostObjectKeyConstructor(DefaultKeyConstructor):
#     retrieve_sql = RetrieveSqlQueryKeyBit()
#     updated_at = PostUpdatedAtKeyBit()
#
#
# class CommentListKeyConstructor(DefaultKeyConstructor):
#     list_sql = ListSqlQueryKeyBit()
#     pagination = PaginationKeyBit()
#     updated_at = CommentUpdatedAtKeyBit()


class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    博客文章视图集

    - list: 返回博客文章列表
    - retrieve: 返回博客文章详情
    - list_comments: 返回博客文章下的评论列表
    - list_archive_dates: 返回博客文章归档日期列表
    """
    queryset = Post.objects.all()
    # pagination_class = LimitOffsetPagination
    pagination_class = PageNumberPagination # 可省略，settings 中配置了，只要 ListModelMixin 都实现了分页
    permission_classes = [AllowAny]

    # 序列化设置
    serializer_class = PostListSerializer
    serializer_class_table = {
        "list": PostListSerializer,
        "retrieve": PostRetrieveSerializer,
    }

    # 过滤器设置
    # API 在返回结果时，drf 会调用设置的 backend（这里是 DjangoFilterBackend）的 filter 方法对 get_queryset 方法返回的结果进行进一步的过滤
    # DjangoFilterBackend 会依据 filterset_class（这里是 PostFilter）中定义的过滤规则来过滤查询结果集
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_serializer_class(self):
        return self.serializer_class_table.get(self.action, super().get_serializer_class())

    # @cache_response(timeout=5 * 60, key_func=PostListKeyConstructor())
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)
    #
    # @cache_response(timeout=5 * 60, key_func=PostObjectKeyConstructor())
    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)

    # 还可以在 action 中设置所有 ViewSet 类所支持的类属性，例如 serializer_class、pagination_class、permission_classes 等
    # 用于覆盖类视图中设置的属性值
    # 最终自动生成的接口路由就是 /posts/archive/dates/
    # 如果我们设置 detail 为 True，那么生成的接口路由就是 /posts/<int:pk>/archive/dates/
    @swagger_auto_schema(responses={200: "归档日期列表，时间倒序排列。例如：['2020-08', '2020-06']。"})
    @action(
        methods=["GET"],
        detail=False,
        url_path="archive/dates",
        url_name="archive-date",
        filter_backends=[],
        pagination_class=None,
    )
    def list_archive_dates(self, request, *args, **kwargs):
        dates = Post.objects.dates("created_time", "month", order="DESC")   # 已去重
        date_field = DateField()
        data = [date_field.to_representation(date)[:7] for date in dates]
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,  # /posts/:id/comments/
        url_path="comments",
        url_name="comment",
        filter_backends=[],  # 移除从 PostViewSet 自动继承的 filter_backends，这样 drf-yasg 就不会生成过滤参数
        suffix="List",  # 将这个 action 返回的结果标记为列表，否则 drf-yasg 会根据 detail=True 将结果误判为单个对象
        pagination_class=LimitOffsetPagination,
        serializer_class=CommentSerializer,
    )
    def list_comments(self, request, *args, **kwargs):
        # 根据 URL 传入的参数值（文章 id）获取到博客文章记录
        post = self.get_object()
        # 获取文章下关联的全部评论
        queryset = post.comment_set.all().order_by("-created_time")
        # 对评论列表进行分页，根据 URL 传入的参数获取指定页的评论
        page = self.paginate_queryset(queryset)
        # 序列化评论
        serializer = self.get_serializer(page, many=True)
        # 返回分页后的评论列表
        return self.get_paginated_response(serializer.data)


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    博客文章分类视图集

    - list: 返回博客文章分类列表
    """

    serializer_class = CategorySerializer
    # 关闭分页
    pagination_class = None

    def get_queryset(self):
        return Category.objects.all().order_by("name")


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    博客文章标签视图集

    - list: 返回博客文章标签列表
    """

    serializer_class = TagSerializer
    # 关闭分页
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all().order_by("name")