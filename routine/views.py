from rest_framework.views import APIView
from rest_framework.response import Response
from routine.models import NoSQL
from routine.utils.handle_json import get_json, make_response, RequestInvalid
from routine import serializers
from supplyAuth.models import User as UserModel
from . import models

class Hello(APIView):
    def get(self, request, format=None):
        Item = {'id': 1, 'name': 'MO'}
        NoSQL.User.create(Item)
        return Response('hello')
    
class Read(APIView):
    def get(self, request, format=None):
        my_model = NoSQL.User.get(id=1)
        if my_model:
            print(my_model['name'])
        return Response('hello')
    
class Delete(APIView):
    def get(self, request, format=None):
        NoSQL.User.delete(id=1)
        return Response('hello')

class Routine(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        user_id = 1 if(request.user.id is None) else request.user.id
        user = UserModel.objects.get(id=user_id)
        try:
            datas: dict = get_json(request, serializers.Routine_create)
        except RequestInvalid:
            return make_response(status_code=400)
        try: 
            r = models.Routine(
                    user_id = user,
                    dow = datas['dow'],
                    start_time = datas['start_time'],
                    end_time = datas['end_time'],
                    title = datas['title'],
                    subtitle = datas['subtitle'],
                    public = datas['public'],
                    notification = datas['notification'],
                    icon = datas['icon']
                )
            r.save()
            datas = {'routine_id': r.id}
        except Exception as e:
            datas = {}
            print(f'{e}')
            raise e
        return make_response(data = datas)
    
    def patch(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Routine_update)
        except RequestInvalid:
            return make_response(status_code=400)
        try: 
            # データベースから Routine オブジェクトを取得
            r = models.Routine.objects.get(id=datas['routine_id'])
            # update
            r.dow = datas.get('dow', r.dow)
            r.start_time = datas.get('start_time', r.start_time)
            r.end_time = datas.get('end_time', r.end_time)
            r.title = datas.get('title', r.title)
            r.subtitle = datas.get('subtitle', r.subtitle)
            r.is_published = datas.get('public', r.is_published)
            r.is_notified = datas.get('is_notified', r.is_notified)
            r.icon = datas.get('icon', r.icon)
            r.save()
        except models.Routine.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Routine not found'})
        except:
            return make_response(status_code=400)
        datas = {'routine_id': r.id}
        return make_response(data = datas)
    
    def delete(self, request, format=None):
        try:
            datas = get_json(request, serializers.Routine_delete)
        except RequestInvalid:
            return make_response(status_code=400)
        try:
            r = models.Routine.objects.get(id=datas['routine_id'])
            r.delete()
        except models.Routine.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Routine not found'})
        except:
            return make_response(status_code=400)
        return make_response(status_code=200, data={'message': 'Routine deleted successfully'})
    

class Task(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Routine_create)
        except RequestInvalid:
            return make_response(status_code=400)
        try: 
            t = models.Task(
                    routine_id = datas['routine_id'],
                    title = datas['title'],
                    detail = datas['detail'],  
                    icon = datas['icon'],  
                    required_time = datas['required_time'],  
                    is_notified = datas['is_notified']
                )
            t.save()
        except:
            pass
        datas = {'task_id': t.id}
        print(datas)
        return make_response(data = datas)
    
    def patch(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Task_update)
        except RequestInvalid:
            return make_response(status_code=400)
        try: 
            t = models.Task.objects.get(id=datas['task_id'])
            t.routine_id = datas.get('routine_id', t.routine_id)
            t.title = datas.get('title', t.title)
            t.detail = datas.get('detail', t.detail)
            t.icon = datas.get('icon', t.icon)
            t.required_time = datas.get('required_time', t.required_time)
            t.is_notified = datas.get('notification', t.is_notified)
            t.save()
        except models.Task.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task not found'})
        except:
            return make_response(status_code=400)
        datas = {'task_id': t.id}
        return make_response(data = datas)

    def delete(self, request, format=None):
        try:
            datas = get_json(request, serializers.Task_delete)
        except RequestInvalid:
            return make_response(status_code=400)
        try:
            t = models.Task.objects.get(id=datas['task_id'])
            t.delete()
        except models.Task.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task not found'})
        except:
            return make_response(status_code=400)
        return make_response(status_code=200, data={'message': 'Task deleted successfully'})