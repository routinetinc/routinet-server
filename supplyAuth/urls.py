from django.urls import include, path
from rest_framework import routers
from routine import views

urlpatterns = [
    path('auth/', include('rest_framework.urls', namespace='rest_framework_auth'))
]

urlpatterns += [
    path('hello/', views.Hello.as_view()),
]