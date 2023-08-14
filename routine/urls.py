from django.urls import include, path
from rest_framework import routers
from routine import views
from routine.views_package.timetree import *

urlpatterns = [
    path('routine/', include('rest_framework.urls', namespace='routine'))
]

urlpatterns += [
    path('hello/', views.Hello.as_view()),
    path('read/', views.Read.as_view()),
    path('delete/', views.Delete.as_view()),
    path('routine/', views.Routine.as_view()),
    path('task/', views.Task.as_view()),
    path('timetree/before/get/', TimeTreeBefore.as_view()),
    path('timetree/after/get/', TimeTreeAfter.as_view()),
    path('timetree/before_after/get/', TimeTreeAfterToBefore.as_view()),
    path('task/finish/', views.NoAvailableTask.as_view()),
    path('task/minicomment/', views.MiniComment.as_view()),
    path('routine_task/', views.RoutineTask.as_view()),
]