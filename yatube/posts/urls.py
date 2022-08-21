from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('500/', views.server_error, name='500'),
    path('404/', views.page_not_found, name='404'),
    path('403/', views.failure, name='403'),
    path('404csrf/', views.page_not_found, name='404csrf'),

    path('create/',
         views.post_create,
         name='post_create'),

    path('follow/',
         views.follow_index,
         name='follow_index'),

    path('<str:username>/',
         views.profile,
         name='profile'),

    path('profile/<str:username>/', views.profile, name='profile'),

    path('group/<slug:slug>/',
         views.group_posts,
         name='group_list'),

    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

    path('<str:username>/<int:post_id>/',
         views.post_detail,
         name='post_detail'),

    path('<str:username>/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),

    path('<str:username>/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),

    path('<str:username>/follow/',
         views.profile_follow,
         name='profile_follow'),

    path('<str:username>/unfollow/',
         views.profile_unfollow,
         name='profile_unfollow'),

    path('<str:username>/unfollow/',
         views.profile_unfollow,
         name='profile_unfollow'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
