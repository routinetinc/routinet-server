from rest_framework.views import APIView
from datetime import datetime, timedelta
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers
from supply_auth.models import User as UserModel
from django.http import JsonResponse, HttpRequest


class Routine(APIView):
    def get(self, request: HttpRequest, format=None):
        try:
            routine_id = request.query_params.get('routine_id')
            # print(f"Routine ID received: {routine_id}")

            if routine_id is not None:
                try:
                    routine = models.Routine.objects.get(id=routine_id)
                    # print(f"Routine found: {routine}")
                    # print("type of routine = ", type(routine))

                    # Check if the calculate_consecutive_days method exists and call it
                    consecutive_days = routine.calculate_consecutive_days() 
                    print(f"Consecutive days calculated: {consecutive_days}")

                except models.Routine.DoesNotExist:
                    print(f"No routine found with ID: {routine_id}")
                    return make_response(status_code=404, data={'message': 'Routine not found'})
            else:
                print(f"No routine ID provided in the request")
                return make_response(status_code=400, data={'message': 'No routine ID provided'})

            tasks = models.Task.objects.filter(routine_id=routine).order_by('id')
            # print(f"Tasks found: {tasks.count()}")

            tasks_data = []
            for task in tasks:
                # print("task = ", task)
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
                # print(f"Task data added: {task_data}")

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
        user_id = 1 if(request.user.id is None) else request.user.id
        user = UserModel.objects.get(id=user_id)

        #dowのリストを、[0, 1, 2, 3, 4, 5, 6]の形式で、その日から順番に用意
        now = datetime.now()
        dow_list = [(now + timedelta(days=i)).weekday() for i in range(7)]

        routines_data = {}
        routines_by_day = {
            "mon": [],
            "tue": [],
            "wed": [],
            "thu": [],
            "fri": [],
            "sat": [],
            "sun": []
        }
        day_of_week = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

        for dow in dow_list:
            #SQL文の実行結果をDjangoのインスタンスとして返す
            routines = models.Routine.objects.raw(
            
                #models.Routine.objects.raw(): Djangoで生のSQLクエリを実行。
                # SELECT * FROM routine_routine: ルーティンテーブルから全カラムを取得。
                # WHERE user_id_id = %s: ユーザーIDに基づくレコードのフィルタリング。
                # AND (dow & %s) != 0: 曜日情報（dow）をビット単位で解析し、該当するレコードをフィルタリング。
                # ORDER BY start_time: 結果をルーティンの開始時間順にソート。

                "SELECT * FROM routine_routine WHERE user_id_id = %s AND (dow & %s) != 0 ORDER BY start_time",

                # [user.id, 2**dow]: フィルタリングと解析のためのパラメータを渡す。
                [user.id, 2**dow])

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
                            "is_notified": task.is_notified,
                            "is_achieved": is_achieved,
                        })
                    routines_data[str(routine.id)] = {
                        "start_time": routine.start_time,
                        "end_time": routine.end_time,
                        "title": routine.title,
                        "subtitle": routine.subtitle,
                        "is_published": routine.is_published,
                        "is_notified": routine.is_notified,
                        "tasks": task_data
                    }
                routines_by_day[day_of_week[dow]].append(str(routine.id))


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
        return make_response(status_code=200, data=data)