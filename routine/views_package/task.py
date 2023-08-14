from rest_framework.views import APIView
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers

class Task(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Task_create)
        except RequestInvalid:
            return make_response(status_code=400)
        try: 
            
            try:
                routine_instance = models.Routine.objects.get(id=datas['routine_id'])
            except models.Routine.DoesNotExist:
                return make_response(status_code=404, data={'message': 'Routine not found'})
            
            t = models.Task(
                    routine_id = routine_instance,
                    title = datas['title'],
                    detail = datas['detail'],  
                    icon = datas['icon'],  
                    required_time = datas['required_time'],  
                    is_notified = datas['is_notified']
                )
            t.save()
        except Exception as e:
            print(e)
        datas = {'task_id': t.id}
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