from django.urls import include, path
from rest_framework import routers
from feed import views

urlpatterns = [
    path('user/create/', views.UserCreate.as_view()),
    path('interest/create', views.InteresstCATCreate.as_view()),
    path('interest/update', views.InterestCATUpdate.as_view()),
    path('user/read/', views.UserRead.as_view()),
    path('user/delete/', views.UserDelete.as_view()),
]