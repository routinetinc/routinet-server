from rest_framework.views import APIView
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers
from django.utils import timezone


class NoAvailableTask(APIView):
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