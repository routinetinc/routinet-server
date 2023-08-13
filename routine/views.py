from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from routine.models import NoSQL
from routine.utils.handle_json import get_json, make_response, RequestInvalid
from routine import serializers
from supplyAuth.models import User as UserModel
from . import models
from datetime import datetime, timedelta
from django.db.models import Q


class Hello(APIView):
    def get(self, request, format=None):
        Item = {'id': 1, 'name': 'MO'}
        NoSQL.User.create(Item)
        return Response('hello')
    
class Read(APIView):
    def get(self, request, format=None):
        my_model = NoSQL.User.get(id=1)
        if my_model:
            print(my_model['name'])
        return Response('hello')
    
class Delete(APIView):
    def get(self, request, format=None):
        NoSQL.User.delete(id=1)
        return Response('hello')

class Routine(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        user_id = 1 if(request.user.id is None) else request.user.id
        user = UserModel.objects.get(id=user_id)
        try:
            datas: dict = get_json(request, serializers.Routine_create)
        except RequestInvalid:
            return make_response(status_code=400)
        try: 
            r = models.Routine(
                    user_id = user,
                    dow = datas['dow'],
                    start_time = datas['start_time'],
                    end_time = datas['end_time'],
                    title = datas['title'],
                    subtitle = datas['subtitle'],
                    is_published = datas['is_published'],
                    is_notified = datas['is_notified'],
                    icon = datas['icon']
                )
            r.save()
            datas = {'routine_id': r.id}
        except Exception as e:
            datas = {}
            raise e
        return make_response(data = datas)
    
    def patch(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Routine_update)
        except RequestInvalid:
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
            r.save()
        except models.Routine.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Routine not found'})
        except:
            return make_response(status_code=400)
        datas = {'routine_id': r.id}
        return make_response(data = datas)
    
    def delete(self, request, format=None):
        try:
            datas = get_json(request, serializers.Routine_delete)
        except RequestInvalid:
            return make_response(status_code=400)
        try:
            r = models.Routine.objects.get(id=datas['routine_id'])
            r.delete()
        except models.Routine.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Routine not found'})
        except:
            return make_response(status_code=400)
        return make_response(status_code=200, data={'message': 'Routine deleted successfully'})
    

class Task(APIView):
    def get(self, request, format=None):
        pass
    
    def post(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.Task_create)
        except RequestInvalid:
            return make_response(status_code=400)
        try: 
            
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
        except Exception as e:
            print(e)
        datas = {'task_id': t.id}
        return make_response(data = datas)
    
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
        except:
            return make_response(status_code=400)
        datas = {'task_id': t.id}
        return make_response(data = datas)

    def delete(self, request, format=None):
        try:
            datas = get_json(request, serializers.Task_delete)
        except RequestInvalid:
            return make_response(status_code=400)
        try:
            t = models.Task.objects.get(id=datas['task_id'])
            t.delete()
        except models.Task.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task not found'})
        except:
            return make_response(status_code=400)
        return make_response(status_code=200, data={'message': 'Task deleted successfully'})
    
#ログインユーザーの、一週間分のルーティーンとタスクを取得する。
class RoutineTask(APIView):                 
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
                        latest_task_record = models.TaskRecord.objects.filter(task_id=task.id).order_by('-when').first()
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


class NoAvailableTask(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        try:
            data = get_json(request, serializers.TaskRecord_create)  # Assuming TaskRecord_create is a valid serializer -> ok by shogo
        except RequestInvalid:
            return make_response(status_code=400)

        try:
            task = models.Task.objects.get(id=data["task_id"])
        except models.Task.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task not found'})
            
        try:
            task_record = models.TaskRecord(task_id=task, done_time=data.get("done_time"))
            task_record.save()
        except:
            pass  # You may want to handle exceptions properly here

        data = {"task_record_id": task_record.id}
        return make_response(status_code=1, data=data)

class MiniComment(APIView):
    def get(self, request, format=None):
        pass

    def post(self, request, format=None):
        try:
            data = get_json(request, serializers.MiniComment_create)
        except RequestInvalid:
            return make_response(status_code=400)

        try:
            task_record = models.TaskRecord.objects.get(id=data["task_record_id"])
        except models.TaskRecord.DoesNotExist:
            return make_response(status_code=404, data={'message': 'Task_record not found'})

        try:
            minicomment = models.Minicomment(task_record_id=task_record, comment=data["comment"])
            minicomment.save()
        except models.TaskRecord.DoesNotExist:
            pass

        data = {"task_record_id": str(minicomment.task_record_id)}
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
        except models.TaskRecord.DoesNotExist:
            return make_response(status_code=400, data={"message": "Minicomment not found."})

        data = {"task_record_id": str(minicomment.task_record_id)}
        return make_response(status_code=200, data=data)
