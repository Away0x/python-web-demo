from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "name",
            "email",
            "url",
            "text",
            "created_time",
            "post",
        ]
        # 用于指定只读字段的列表，由于 created_time 是自动生成的，用于记录评论发布时间，因此声明为只读的，不允许通过接口进行修改
        read_only_fields = [
            "created_time",
        ]
        # 指定传入每个序列化字段的额外参数，这里给 post 序列化字段传入了 write_only 关键字参数，这样就将 post 声明为只写的字段，
        # 这样 post 字段的值仅在创建评论时需要。而在返回的资源中，post 字段就不会出现
        extra_kwargs = {"post": {"write_only": True}}
