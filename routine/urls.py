from django.urls import include, path
from rest_framework import routers
from routine import views
from routine.views_package.routine import Routine, ReadRoutineAndTask
from routine.views_package.task import Task 
from routine.views_package.no_available_task import NoAvailableTask 
from routine.views_package.mini_comment import MiniComment
from routine.views_package.timetree import TimeTreeAfter, TimeTreeAfterToBefore, TimeTreeBefore

urlpatterns = [
<<<<<<< HEAD
    path('hello/', views.Hello.as_view()),
    path('read/', views.Read.as_view()),
    path('delete/', views.Delete.as_view()),
    path('routine/', views.Routine.as_view()),
    path('task/', views.Task.as_view()),
    path("comment/",views.MiniComment.as_view(),)
=======
    path('routine/', include('rest_framework.urls', namespace='routine'))
]

urlpatterns += [
    path('routine/', Routine.as_view()),
    path('task/', Task.as_view()),
    path('timetree/before/get/', TimeTreeBefore.as_view()),
    path('timetree/after/get/', TimeTreeAfter.as_view()),
    path('timetree/before_after/get/', TimeTreeAfterToBefore.as_view()),
    path('task/finish/', NoAvailableTask.as_view()),
    path('task/minicomment/', MiniComment.as_view()),
    path('routine_task/', ReadRoutineAndTask.as_view()),
>>>>>>> dev
]