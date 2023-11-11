from rest_framework.views import APIView
from datetime import datetime, timedelta
from routine import models, serializers
# from routine.models import Routine, RoutineFinish, Task, TaskFinish
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers
from supply_auth.models import User as UserModel
from django.http import JsonResponse, HttpRequest
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date

class Routine(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        user_id = 1 if(request.user.id is None) else request.user.id
        user = UserModel.objects.get(id=user_id)
        try:
            datas: dict = get_json(request, serializers.Routine_create)
        except RequestInvalid as e:
            return make_response(status_code=400)
        r = models.Routine(
                user_id = user,
                dow = datas['dow'],
                start_time = datas['start_time'],
                end_time = datas['end_time'],
                title = datas['title'],
                subtitle = datas['subtitle'],
                is_published = datas['is_published'],
                is_notified = datas['is_notified'],
                icon = datas['icon'],
                interest_ids = datas['interest_ids']
            )
        r.save()
        datas = {'routine_id': r.id}
        return make_response(data = datas)
    
    def patch(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Routine_update)
        except RequestInvalid as e:
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
            r.interest_ids = datas.get('interest_ids', r.interest_ids)
            r.save()
        except models.Routine.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Routine not found'})
        datas = {'routine_id': r.id}
        return make_response(data = datas)
    
    def delete(self, request, format=None):
        try:
            datas = get_json(request, serializers.Routine_delete)
        except RequestInvalid as e:
            return make_response(status_code=400)
        try:
            r = models.Routine.objects.get(id=datas['routine_id'])
            r.delete()
        except models.Routine.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Routine not found'})
        return make_response(status_code=200, data={'message': 'Routine deleted successfully'})


#ログインユーザーの、一週間分のルーティーンとタスクを取得する。
class ReadRoutineAndTask(APIView):
    def get(self, request, format=None):
        user_id = 1 if request.user.id is None else request.user.id
        user = UserModel.objects.get(id=user_id)
        print("1")

        # Parse the week_start query parameter to a date object
        week_start_str = request.query_params.get('week_start')
        if week_start_str and len(week_start_str) == 8:  # Check if the parameter is present and of the correct length
            week_start_formatted_str = f"{week_start_str[:4]}-{week_start_str[4:6]}-{week_start_str[6:]}"
            week_start_date = parse_date(week_start_formatted_str)
            print(week_start_date)
        else:
            # Handle the case where week_start is not provided or not properly formatted
            return make_response(status_code=400, data={'message': 'Invalid week_start parameter'})

        # Calculate the start (Monday) and end (Sunday) of the week
        start_of_week = week_start_date - timedelta(days=week_start_date.weekday())
        print(start_of_week)

        end_of_week = start_of_week + timedelta(days=6)
        print("1")

        routines_data = {}
        routines_by_day = {day: [] for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']}
        print("1")

        # Iterate over each day of the week starting from Monday
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            day_code = day_date.weekday()
            day_name = day_date.strftime('%a').lower()
            print(day_date, day_code, day_name)

            routines = models.Routine.objects.filter(
                user_id=user_id,
                dow=day_code  # Assuming 'dow' can be compared directly to 'day_code'. Adjust if needed.
            ).order_by('start_time')
            print("1")
            for routine in routines:
                if str(routine.id) not in routines_data:
                    tasks = models.Task.objects.filter(routine_id=routine).order_by('id')
                    task_data = []
                    for task in tasks:
                        latest_task_record = models.TaskFinish.objects.filter(task_id=task.id).order_by('-when').first()
                        is_achieved = latest_task_record.is_achieved if latest_task_record else False
                        task_data.append({
                            "task_id": task.id,
                            "title": task.title,
                            "detail": task.detail,
                            "required_time": task.required_time,
                            "is_achieved": is_achieved,
                            # "tag_id": routine.tag_id.id if routine.tag_id else None,  # Assuming `tag_id` is a foreign key to another model
                            # "real_time": routine.is_real_time,  # Assuming `is_real_time` corresponds to `real_time`
                            # "tag_name": routine.tag_id.name if routine.tag_id else '',  # Replace with actual field name for the tag's name
                            # "consecutive_days": routine.calculate_consecutive_days(),  # Call the method on the routine instance
                        })
                    routines_data[str(routine.id)] = {
                        "start_time": routine.start_time,
                        "end_time": routine.end_time,
                        "title": routine.title,
                        "tag_id": routine.tag_id.id if routine.tag_id else None,
                        "tasks": task_data
                    }
                routines_by_day[day_name].append(str(routine.id))
        print("1")

        # Build the data structure for the response
        data = {
            "mon": routines_by_day["mon"],
            "tue": routines_by_day["tue"],
            "wed": routines_by_day["wed"],
            "thu": routines_by_day["thu"],
            "fri": routines_by_day["fri"],
            "sat": routines_by_day["sat"],
            "sun": routines_by_day["sun"],
            "routines": routines_data
        }
        return make_response(status_code=1, data=data)