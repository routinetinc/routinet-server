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
    routine_id = data['routine_id']
    if(acquisition_range == -1):
        n, m, end = 0, -7, 7
    elif(acquisition_range == 0):
        n, m, end = 7, -7, 14
    elif(acquisition_range == 1):
        n, m, end = 7, 0, 7
    else:
        n, m, end = 0, 0, 0
    start_day: datetime = data['day'] + timedelta(days=n)
    end_day: datetime = start_day + timedelta(days=m)
    tasks = models.Task.objects.filter(routine_id=routine_id).order_by('-id')

    subquery = models.TaskRecord.objects.filter(task_id=OuterRef('task_id'), when__range=[end_day, start_day])
    task_records = models.TaskRecord.objects.filter(task_id__in=tasks)\
                                            .annotate(matching_task=Exists(subquery))\
                                            .filter(matching_task=True).order_by('-when')
    days = []
    for i in range(end):
        day = start_day - timedelta(days=i)
        day_str = day
        day_tasks = []
        for task_record in task_records:
            if task_record.when.date() == day.date():
                task_comment = models.TaskComment.objects.filter(task_record_id=task_record.id).first()
                comment = task_comment.comment if task_comment else None
                day_tasks.append({
                    'task_recode_id': str(task_record.id),
                    'finish_time': conv_datetime_iso(task_record.when),
                    'done_time': task_record.done_time,
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
    
