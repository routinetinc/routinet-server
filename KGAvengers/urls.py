from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path("auth/", include("supplyAuth.urls")),
    path("routine/", include("routine.urls")),
    path("comment/",include("routine.urls"))
=======
    path('auth/', include('supplyAuth.urls')),
    path('routine/', include('routine.urls')),
    path('feed/', include('feed.urls')),
>>>>>>> dev
]
