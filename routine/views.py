from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from routine.models import NoSQL

class Hello(APIView):
    def get(self, request, format=None):
        Item = {'id': 1, 'name': "MO"}
        NoSQL.User.create(Item)
        return Response("hello")
    
class Read(APIView):
    def get(self, request, format=None):
        my_model = NoSQL.User.get(id=1)
        if my_model:
            print(my_model["name"])
        return Response("hello")
    
class Delete(APIView):
    def get(self, request, format=None):
        NoSQL.User.delete(id=1)
        return Response("hello")