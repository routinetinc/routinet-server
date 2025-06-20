from rest_framework.views import APIView
from datetime import datetime, timedelta
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine.utils.conv_time_fmt import conv_datetime_iso
from routine import serializers
from django.db.models import Exists, OuterRef

def _timetree(request, acquisition_range):
    ''' one week before ~ specified date: -1, one week before ~ one week after: 0, specified date ~ one week after: 1 '''
    try: 
        data = get_json(request, serializers.TimeTree)
    except RequestInvalid:
        return make_response(status_code=400) 
    if(acquisition_range == -1):
        delta_start_day, delta_end_day, loop_end = 0, -7, 7
    elif(acquisition_range == 0):
        delta_start_day, delta_end_day, loop_end = 7, -7, 14
    elif(acquisition_range == 1):
        delta_start_day, delta_end_day, loop_end = 7, 0, 7
    else:
        delta_start_day, delta_end_day, loop_end = 0, 0, 0

    routine_id = data['routine_id']
    tasks = models.Task.objects.filter(routine_id=routine_id).order_by('-id')

    start_day: datetime = data['day'] + timedelta(days=delta_start_day)
    end_day:   datetime = start_day   + timedelta(days=delta_end_day)

    subquery     = models.TaskFinish.objects.filter(task_id=OuterRef('task_id'), when__range=[end_day, start_day])
    task_finishs = models.TaskFinish.objects.filter(task_id__in=tasks) \
                                            .annotate(matching_task=Exists(subquery)) \
                                            .filter(matching_task=True) \
                                            .order_by('-when')
    days = []
    for i in range(loop_end):
        day = start_day - timedelta(days=i)
        day_str = day
        day_tasks = []
        for task_finish in task_finishs:
            if task_finish.when.date() == day.date():
                task_comment = models.Minicomment.objects.filter(task_finish_id=task_finish.id).first()
                comment = task_comment.comment if task_comment else None
                day_tasks.append({
                    'task_finish_id': str(task_finish.id),
                    'finish_time': conv_datetime_iso(task_finish.when),
                    'done_time': task_finish.done_time,
                    'comment': comment
                })
        days.append({
            'day': conv_datetime_iso(day_str),
            'tasks': day_tasks
        })
    data = {
        'data': {
            'timetree': {
                'routine_id': routine_id,
                'days': days
            }
        }
    }
    return make_response(data=data)

    

class TimeTreeBefore(APIView):
    def post(self, request, format=None):
        return _timetree(request, -1)

class TimeTreeAfterToBefore(APIView):
    def post(self, request, format=None):
        return _timetree(request, 0)
    
class TimeTreeAfter(APIView):
    def post(self, request, format=None):
        return _timetree(request, 1)
    
