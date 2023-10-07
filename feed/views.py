from feed.models import Cache
from rest_framework.views import APIView
from rest_framework.response import Response
from feed.structure import Data
from routine.utils.handle_json import make_response

class UserCreate(APIView):
    def get(self, request, format=None):
        Item = {'user_id': 3, 'created': '2023-08-26','data':{'content_id':4}}
        Cache.User.create(Item = Item)
        return Response('hello')
    
class UserRead(APIView):
    def get(self, request, format=None):
        key = {'user_id':3,
               'created':'2023-08-26'}
        my_model = Cache.User.get(key)
        if my_model:
            print(my_model)
        else:
            print("なし")
        return Response('hello')
    
class UserDelete(APIView):
    def get(self, request, format=None):
        key = {'user_id':3,
               'created':'2023-08-26'}
        Cache.User.delete(key)
        return Response('hello')
    
class InteresstCATCreate(APIView):
    def get(self, request, format=None):
        data = Data(0,550,3)
        Cache.InterestCAT.update(data = data)
        Cache.InterestCAT.query(data = data)
        return make_response({'response':'hello'})

class InterestCATDelete(APIView):
    def get(self, request, format=None):
        data = Data(0,0,0)
        Cache.InterestCAT.delete(data = data)
        return Response('hello')