from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('supply_auth.urls')),
    path('routine/', include('routine.urls')),
    path('feed/', include('feed.urls')),
]
