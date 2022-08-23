from django.contrib import admin


@admin.register
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)


@admin.register
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


@admin.register
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'post', 'author', 'text')
