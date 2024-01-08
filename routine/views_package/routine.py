from rest_framework.views import APIView
from datetime import datetime, timedelta
from routine import models, serializers
# from routine.models import Routine, RoutineFinish, Task, TaskFinish
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers
from supply_auth.models import User as UserModel
from routine.api_document import decorators
from django.http import JsonResponse, HttpRequest
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.db import connection
from routine.models import Routine, RoutineFinish, Task, TaskFinish
from routine.serializers import RoutineFinishSerializer, ShareRegister
from django.utils import timezone
from django.db.models import Sum

class Routine(APIView):
    def get(self, request: HttpRequest, format=None):
        try:
            routine_id = request.query_params.get('routine_id')
            # print(f"Routine ID received: {routine_id}")

            if routine_id is not None:
                try:
                    routine = models.Routine.objects.get(id=routine_id)
                    consecutive_days = routine.calculate_consecutive_days() 
                    print(f"Consecutive days calculated: {consecutive_days}")

                except models.Routine.DoesNotExist:
                    print(f"No routine found with ID: {routine_id}")
                    return make_response(status_code=404, data={'message': 'Routine not found'})
            else:
                print(f"No routine ID provided in the request")
                return make_response(status_code=400, data={'message': 'No routine ID provided'})

            tasks = models.Task.objects.filter(routine_id=routine).order_by('id')

            tasks_data = []
            for task in tasks:
                latest_task_finish = models.TaskFinish.objects.filter(task_id=task).order_by('-when').first()
                is_achieved = latest_task_finish.is_achieved if latest_task_finish else False
                task_data = {
                    "task_id": task.id,
                    "title": task.title,
                    "detail": task.detail,
                    "required_time": task.required_time,
                    "is_achieved": is_achieved,
                }
                tasks_data.append(task_data)

            routine_data = {
                "routine_id": routine.id,
                "start_time": routine.start_time,  
                "end_time": routine.end_time,
                "title": routine.title,
                "tag_name": "foo",
                "real_time": True,
                "consecutive_days": consecutive_days,
                "dow": routine.dow,
                "tasks": tasks_data
            }
            print(f"Final routine data to be sent: {routine_data}")

            return make_response(status_code=1, data=routine_data)
        
        except Routine.DoesNotExist:
            print("Routine does not exist for the given ID.")
            return make_response(status_code=404, data={'message': 'Routine not found'})
        except RequestInvalid as e:
            print(f"Request is invalid: {e}")
            return make_response(status_code=400, data={'message': str(e)})
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return make_response(status_code=500, data={'message': str(e)})
    
    @decorators.routine_post_schema
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
    
    @decorators.routine_patch_schema
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
    
    @decorators.routine_delete_schema
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
    @decorators.readroutineandtask_get_schema               
    def get(self, request, format=None):
        user_id = 1 if request.user.id is None else request.user.id
        user = UserModel.objects.get(id=user_id)

        # Parse the week_start query parameter to a date object
        week_start_str = request.query_params.get('week_start')
        if week_start_str and len(week_start_str) == 8:  # Check if the parameter is present and of the correct length
            week_start_formatted_str = f"{week_start_str[:4]}-{week_start_str[4:6]}-{week_start_str[6:]}"
            week_start_date = parse_date(week_start_formatted_str)
        else:
            # Handle the case where week_start is not provided or not properly formatted
            return make_response(status_code=400, data={'message': 'Invalid week_start parameter'})

        # Calculate the start (Monday) and end (Sunday) of the week
        start_of_week = week_start_date - timedelta(days=week_start_date.weekday())

        end_of_week = start_of_week + timedelta(days=6)

        routines_data = {}
        routines_by_day = {day: [] for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']}

        # Iterate over each day of the week starting from Monday
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            day_code = day_date.weekday()
            day_name = day_date.strftime('%a').lower()
            print(day_date, day_code, day_name)

            # Create a bitwise mask for the day_code
            day_mask = 1 << day_code
            print(day_mask)

            try:
                # Raw SQL query to perform bitwise operation
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM routine_routine WHERE user_id_id = %s AND (dow & %s) != 0 ORDER BY start_time",
                        [user_id, day_mask]
                    )
                    routines = cursor.fetchall()

                # If using raw SQL, you may need to manually map the results to Routine objects
                # routines = [map_to_routine(row) for row in routines]  # Implement map_to_routine as needed

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return make_response(status_code=500, data={'message': str(e)})
            print(routines)
        

            for row in routines:
                print("row is ", row)
                # Create a Routine instance from the tuple
                routine = models.Routine(
                    id=row[0],
                    interest_ids=row[1],
                    goal_id=row[2],
                    dow=row[3],
                    start_time=row[4],
                    end_time=row[5],
                    title=row[6],
                    subtitle=row[7],
                    icon=row[8],
                    is_published=row[9],
                    is_notified=row[10],
                    bookmark_num=row[11],
                    is_real_time=row[12],
                    tag_id_id=row[13],  # Assuming the foreign key field for Tag
                    user_id_id=row[14]  # Assuming the foreign key field for User
                )
                print("routine is ", routine)

                # Now you can use the 'routine' object as before
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
                                })
                    routines_data[str(routine.id)] = {
                        "start_time": routine.start_time,
                        "end_time": routine.end_time,
                        "title": routine.title,
                        "tag_id": routine.tag_id.id if routine.tag_id else None,
                        "tag_name": routine.tag_id.name if routine.tag_id else '',  # Replace with actual field name for the tag's name
                        "real_time": routine.is_real_time,  # Assuming `is_real_time` corresponds to `real_time`
                        "consecutive_days": routine.calculate_consecutive_days(),  # Call the method on the routine instance
                        "tasks": task_data,
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