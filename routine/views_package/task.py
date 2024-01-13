from rest_framework.views import APIView
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers
from django.utils import timezone
from routine.api_document import decorators

class Task(APIView):
    def get(self, request, format=None):
        pass
    
    @decorators.task_post_schema
    def post(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Task_create)
        except RequestInvalid as e:
            return make_response(status_code=400) 
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
        datas = {'task_id': t.id}
        return make_response(data = datas)
    
    @decorators.task_patch_schema
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
        datas = {'task_id': t.id}
        return make_response(data = datas)

    @decorators.task_delete_schema
    def delete(self, request, format=None):
        try:
            datas = get_json(request, serializers.Task_delete)
        except RequestInvalid as e:
            return make_response(status_code=400)
        try:
            t = models.Task.objects.get(id=datas['task_id'])
            t.delete()
        except models.Task.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task not found'})
        return make_response(status_code=200, data={'message': 'Task deleted successfully'})
    
class NoAvailableTask(APIView):
    @decorators.no_available_task_post_schema
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        try:
            data = get_json(request, serializers.TaskFinish_create)  # Assuming TaskFinish_create is a valid serializer
        except RequestInvalid as e:
            return make_response(status_code=400, data={'message': str(e)})
        
        try:
            task = models.Task.objects.get(id=data["task_id"])
        except models.Task.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task not found'})

        task_finish = models.TaskFinish.objects.create(
            task_id=task,
            done_time=data.get("done_time"),
            when=timezone.now()
        )
        print("task finish is created.")

        today = timezone.now().date()
        now = timezone.now()
        print(task.routine_id)

        today = timezone.now().date()
        now = timezone.now()

        routine_finish, created = models.RoutineFinish.objects.get_or_create(
            routine_id=task.routine_id,
            when__date=today,
            defaults={
                'is_achieved': False,
                'when': now,
                'icon': '',            
                'memo': '',            
                'done_time': 0,        
                'like_num': 0,         
                'share': True             }
        )

        if not created:
            routine_finish.when = now
            routine_finish.save()
        print("end routine finish")
        if created:
            print("A new RoutineFinish object was created.")
        else:
            print("An existing RoutineFinish object was retrieved.")


        return make_response(status_code=1, data={"task_finish_id": task_finish.id})