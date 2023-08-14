from django.urls import include, path
from rest_framework import routers
from payment import views

urlpatterns = [
    path('payment/', include('rest_framework.urls', namespace='routine'))
]

urlpatterns += [
    path('', views.CreatePayment.as_view()),
]