from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from auths import views

urlpatterns = [
    path('token/', views.GetToken.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]