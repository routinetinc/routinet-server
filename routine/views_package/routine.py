import time
from rest_framework.views import APIView
from datetime import datetime, timedelta
from routine import models, serializers
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from routine import serializers
from supplyAuth.models import User as UserModel
from django.utils import timezone

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
                icon = datas['icon']
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

        # 現在の日付を取得し、その週の月曜日の日付を計算
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        # その週の月曜から日曜までの日付のリストを作成
        week_dates = [(monday + timedelta(days=i)).weekday() for i in range(7)]

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

        for dow in week_dates:
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
                    task_data_by_day = {day: [] for day in day_of_week}

                    # 全てのタスクレコードを取得
                    all_task_records = models.TaskRecord.objects.filter(task_id__in=[task.id for task in tasks]).order_by('-when')
                    
                    for task in tasks:
                        # 各曜日に一致するタスクレコードをフィルタリング
                        for day in day_of_week:
                            start_of_day = timezone.make_aware(datetime.combine(week_dates[day_of_week.index(day)], time.min))
                            end_of_day = timezone.make_aware(datetime.combine(week_dates[day_of_week.index(day)], time.max))

                            task_records_for_day = all_task_records.filter(
                                task_id=task.id,
                                when__range=(start_of_day, end_of_day)
                            )

                            is_achieved = any(record.is_achieved for record in task_records_for_day)
                            
                            task_data_by_day[day].append({
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
                        "tasks": task_data_by_day  # 曜日ごとにタスクデータを格納
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