# views.py
from rest_framework.views import APIView
from routine.models import Routine, RoutineFinish, Task, TaskFinish
from routine.serializers import RoutineFinishSerializer, ShareRegister
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from django.utils import timezone
from django.db.models import Sum

class RoutineFinishCreate(APIView):
    def post(self, request, format=None):
        try:
            data = get_json(request, RoutineFinishSerializer)
            routine_id = data.get("routine_id")
            icon = data.get("icon")
            memo = data.get("memo")
            
            try:
                routine = Routine.objects.get(id=routine_id)
            except Routine.DoesNotExist:
                return make_response(status_code=404, data={'message': 'Routine not found'})
            
            total_done_time = TaskFinish.objects.filter(
                routine_id=routine,
                is_achieved=True
            ).aggregate(Sum('done_time'))['done_time__sum'] or 0

            routine_finish = RoutineFinish(
                routine_id=routine,
                icon=icon,
                memo=memo,
                done_time=total_done_time,
                when=timezone.now()
            )
            routine_finish.save()

            consecutive_days = routine.calculate_consecutive_days()

            tasks_data = [
                {"task_name": task_finish.task_id.title, "done_time": task_finish.done_time}
                for task_finish in TaskFinish.objects.filter(routine_id=routine, is_achieved=True)
            ]

            response_data = {
                "routine_finish_id": routine_finish.id,
                "consecutive_days": consecutive_days,
                "tasks": tasks_data
            }
            
            return make_response(status_code=1, data=response_data)
            
        except RequestInvalid as e:
            return make_response(status_code=400, data={'message': str(e)})
        except Exception as e:
            return make_response(status_code=500, data={'message': str(e)})
        
    def patch(self, request, format=None):
        try:
            datas: dict = get_json(request, ShareRegister)
        except RequestInvalid as e:
            return make_response(status_code=400)
        try: 
            # データベースから Routine オブジェクトを取得
            r = RoutineFinish.objects.get(id=datas['routine_finish_id'])
            # update
            r.share = datas.get('share', r.share)
            
            r.save()
        except RoutineFinish.DoesNotExist:
            return make_response(status_code=404, data={'message': 'RoutineFinish not found'})
        datas = {'routine_finish_id': r.id}
        return make_response(data = datas)