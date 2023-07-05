from rest_framework.views import APIView
from rest_framework.response import Response
from routine.models import NoSQL
from routine.utils.handle_json import get_json, make_response, RequestInvalid
from routine import serializers

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

class POST(APIView):
    def post(self, request, format=None):
        try:
            datas = get_json(request,serializers.Task_create)
        except RequestInvalid:
            return make_response(status_code=400)
        print(datas)
        return make_response(data = datas)