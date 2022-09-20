"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include, re_path
from rest_framework import permissions

from blog.feeds import AllPostsRssFeed
from rest_framework.routers import DefaultRouter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from blog.views import PostViewSet, CategoryViewSet, TagViewSet
from comments.views import CommentViewSet

router = DefaultRouter()

router.register(r'posts', PostViewSet, basename='post')
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"comments", CommentViewSet, basename="comment")

# 返回 HTML 格式的文档内容，这样我们就可以直接在浏览器查看到博客的接口文档
schema_view = get_schema_view(
    openapi.Info(
        title="HelloDjango REST framework tutorial API",
        default_version="v1",
        description="HelloDjango REST framework tutorial AP",
        terms_of_service="",
        contact=openapi.Contact(email="zmrenwu@163.com"),
        license=openapi.License(name="GPLv3 License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('blog.urls')),
    path('', include('comments.urls')),

    path('all/rss/', AllPostsRssFeed(), name='rss'),

    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),

    # 文档
    re_path(
        r"swagger(?P<format>\.json|\.yaml)",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
