from rest_framework.views import APIView
from rest_framework.response import Response
from routine.models import NoSQL, Task, Routine
from routine.utils.handle_json import get_json, make_response, RequestInvalid
import json
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

class Routine(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        try:
            datas = get_json(request,serializers.Routine_create)
            r = Routine(dow = datas["dow"],
                    start_time = datas["start_time"],
                    end_time = datas["end_time"],
                    title = datas["title"],
                    subtitle = datas["subtitle"],
                    public = datas["public"],
                    notification = datas["notification"],
                    icon = datas["icon"])
            r.save()
        except RequestInvalid:
            return make_response(status_code=400)
        datas = {"routine_id": r.id}
        print(datas)
        return make_response(data = datas)
    
    def patch(self, request, format=None):
        pass
    
    def delete(self, request, format=None):
        pass
    
class Task(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        try:
            datas = get_json(request, serializers.Routine_create)
            t = Task(title = datas["title"],
                 detail = datas["detail"],
                 required_time = datas["required_time"],
                 notification = datas["notification"])
            t.save()
        except RequestInvalid:
            return make_response(status_code=400)
        datas = {"task_id": t.id}
        print(datas)
        return make_response(data = datas)
    
    def patch(self, request, format=None):
        pass
    
    def delete(self, request, format=None):
        pass
    