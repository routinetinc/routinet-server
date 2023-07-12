from django.urls import include, path
from rest_framework import routers
from routine import views

urlpatterns = [
    path('routine/', include('rest_framework.urls', namespace='routine'))
]

urlpatterns = [
    path('hello/', views.Hello.as_view()),
    path('read/', views.Read.as_view()),
    path('delete/', views.Delete.as_view()),
    path('routine/', views.Routine.as_view()),
    path('task/', views.Task.as_view()),
]