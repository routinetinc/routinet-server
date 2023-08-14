from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('supplyAuth.urls')),
    path('routine/', include('routine.urls')),
    path('payment/', include('payment.urls')),
]
