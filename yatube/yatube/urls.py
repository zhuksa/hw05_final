from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.conf import settings

handler404 = 'posts.views.page_not_found'
handler500 = 'posts.views.server_error'
handler401 = 'posts.views.failure'


urlpatterns = [
    path('about/', include('about.urls', namespace='about')),
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
