from django.contrib import admin

from .models import Post, Group, Follow, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'post', 'author', 'text')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentAdmin)
