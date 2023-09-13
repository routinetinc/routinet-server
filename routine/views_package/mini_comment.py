from rest_framework.views import APIView
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers

class MiniComment(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        try:
            data = get_json(request, serializers.MiniComment_create)
        except RequestInvalid:
            return make_response(status_code=400)

        try:
            task_finish = models.TaskFinish.objects.get(id=data["task_finish_id"])
        except models.TaskFinish.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task_finish not found'})

        try:
            minicomment = models.Minicomment(task_finish_id=task_finish, comment=data["comment"])
            minicomment.save()
        except models.TaskFinish.DoesNotExist:
            pass

        data = {"task_finish_id": str(minicomment.task_finish_id)}
        return make_response(status_code=200, data=data)

    def patch(self, request, format=None):
        try:
            data = get_json(request, serializers.MiniComment_update)
        except RequestInvalid:
            return make_response(status_code=400)

        try:
            minicomment = models.Minicomment.objects.get(id=data["minicomment_id"])
            minicomment.comment = data["comment"]
            minicomment.save()
        except models.TaskFinish.DoesNotExist:
            return make_response(status_code=400, data={"message": "Minicomment not found."})

        data = {"task_finish_id": str(minicomment.task_finish_id)}
        return make_response(status_code=200, data=data)