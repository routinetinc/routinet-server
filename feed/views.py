from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response

class Hello(APIView):
    def get(self, request, format=None):
        Item = {'user_id': 2, 'created': '2023-08-26','data':{'content_id':3}}
        Cache.User.create(Item = Item)
        return Response('hello')
    
class Read(APIView):
    def get(self, request, format=None):
        my_model = Cache.User.get(id=1)
        if my_model:
            print(my_model['name'])
        return Response('hello')
    
class Delete(APIView):
    def get(self, request, format=None):
        Cache.User.delete(id=1)
        return Response('hello')
 
