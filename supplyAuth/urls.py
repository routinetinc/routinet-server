from django.urls import path, re_path, include

from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    re_path('register-by-access-token/' + r'social/(?P<backend>[^/]+)/$', views.register_by_access_token),
    path('authentication-test/', views.authentication_test),
    path('', include('social_django.urls', namespace='social')),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]