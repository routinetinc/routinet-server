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
        except RequestInvalid:
            return make_response(status_code=400)
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
            datas = get_json(request,serializers.Routine_create)
        except RequestInvalid:
            return make_response(status_code=400)
        print(datas)
        return make_response(data = datas)
    
    def patch(self, request, format=None):
        pass
    
    def delete(self, request, format=None):
        pass

class Create_task(APIView):
    def post(self, request, format=None):
        json_data = request.body.decode("utf-8")
        datas = json.loads(json_data)
        data = datas["data"]
        q = Task(title = data["title"],
                 detail = data["detail"],
                 required_time = data["required_time"],
                 notification = data["notification"])
        q.save()
        response_data = {"message": 1,
                         "data": {"task_id": "1"}}
        return JsonResponse(response_data)
    
class Create_routine(APIView):
    def post(self, request, format=None):
        json_data = request.body.decode("utf-8")
        datas = json.loads(json_data)
        data = datas["data"]
        q = Routine(dow = data["dow"],
                    start_time = data["start_time"],
                    end_time = data["end_time"],
                    title = data["title"],
                    subtitle = data["subtitle"],
                    public = data["public"],
                    notification = data["notification"],
                    icon = data["icon"])
        q.save()
        response_data = {"message": 1,
                         "data": {"routine_id": "1"}}
        return JsonResponse(response_data)