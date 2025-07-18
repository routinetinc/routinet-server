from rest_framework.views import APIView
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers


class NoAvailableTask(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        try:
            data = get_json(request, serializers.TaskFinish_create)  # Assuming TaskRecord_create is a valid serializer -> ok by shogo
        except RequestInvalid as e:
            return make_response(status_code=400)
        try:
            task = models.Task.objects.get(id=data["task_id"])
        except models.Task.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task not found'})
            
        task_finish = models.TaskFinish(task_id=task, done_time=data.get("done_time"))
        task_finish.save()

        data = {"task_finish_id": task_finish.id}
        return make_response(status_code=1, data=data)
